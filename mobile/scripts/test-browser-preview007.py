"""Verify visible prototype behaviour; no real emails, uploads or shared writes."""
import argparse, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
parser=argparse.ArgumentParser()
parser.add_argument('--output-dir',type=Path,required=True)
parser.add_argument('--base-url',default='http://127.0.0.1:8775')
parser.add_argument('--api-url',default='http://127.0.0.1:8774')
args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=False)
proof={};errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(args.base_url,wait_until='domcontentloaded')
 page.get_by_role('tab',name='Техника',exact=True).wait_for(timeout=60000)
 expect(page.get_by_role('switch')).to_have_count(0)
 expect(page.get_by_test_id('thumbnail-loaded-demo-milk')).to_be_visible()
 page.evaluate("""() => {
  const key = 'spestovnik-preview-001';
  const state = JSON.parse(localStorage.getItem(key) || '{}');
  localStorage.setItem(key, JSON.stringify({...state, showSamplePhotos: false}));
 }""")
 page.reload()
 expect(page.get_by_test_id('thumbnail-loaded-demo-milk')).to_be_visible()
 proof['thumbnails_visible_with_legacy_opt_out']=True
 expect(page.get_by_role("img", name=re.compile("Символично изображение$")).first).to_be_visible(timeout=15000)
 page.get_by_role('tab',name='Техника',exact=True).click()
 toolbar=page.get_by_test_id('catalog-toolbar')
 page.get_by_role('button',name='Отвори менюто',exact=True).click()
 page.get_by_role('menuitem',name='Търговски обекти',exact=True).click()
 directory=page.get_by_test_id('merchant-directory')
 for name in ['Зора','Technopolis','Technomarket','Techmart','Вали','Ardes','Jar Computers']:
  expect(directory.get_by_text(name,exact=False)).to_be_visible(timeout=15000)
 expect(directory.get_by_role('heading',name='София',exact=True)).to_have_count(3)
 proof['seven_requested_chains_with_recorded_addresses']=True
 page.screenshot(path=str(args.output_dir/'merchant-directory.png'))
 page.get_by_role('tab',name='Техника',exact=True).click()
 page.get_by_label('Търси населено място…',exact=True).fill('Sofia')
 page.get_by_text('София',exact=True).first.click()
 page.get_by_role('tab',name='Горива',exact=True).click()
 for index,name in enumerate(['Бензин 95','Бензин 98+','Дизел','Дизел +','Автогаз']):
  toolbar.get_by_role('button',name=re.compile('^Избрано гориво:')).click()
  page.get_by_role('radio',name=name,exact=True).click()
  expect(page.get_by_text(f'{1.48+index*.1:.2f} €/L',exact=True)).to_be_visible(timeout=10000)
 expect(page.get_by_text('Примерен обект · демонстрационен адрес',exact=True)).to_have_count(6)
 proof['six_requested_stations_and_all_five_price_filters']=True
 page.wait_for_timeout(650);page.screenshot(path=str(args.output_dir/'fuel.png'))
 page.get_by_role('tab',name='Техника',exact=True).click()
 expect(page.get_by_test_id('thumbnail-loaded-demo-laptop')).to_be_visible(timeout=20000)
 expect(page.get_by_role('link', name='Trankiet589 · CC BY-SA 4.0', exact=True)).to_have_count(0)
 search=page.get_by_label('Търси продукт…',exact=True)
 search.fill('Лаптоп')
 page.get_by_role('checkbox',name='Лаптоп (примерна снимка)',exact=True).click()
 search.fill('Смартфон')
 page.get_by_role('checkbox',name='Смартфон (примерна снимка)',exact=True).click()
 page.get_by_role('button',name='Приложи (2)',exact=True).click()
 expect(page.get_by_role('button',name=re.compile('^Добави '))).to_have_count(2)
 proof['multiselect_retains_pending_selection_across_queries']=True
 page.wait_for_timeout(650);page.screenshot(path=str(args.output_dir/'technology.png'))
 search.fill('телевизор')
 page.get_by_role('button',name='Изчисти',exact=True).click()
 search.fill('телевизор')
 page.get_by_role('button',name=re.compile('^Приложи')).click()
 names=page.get_by_role('button',name=re.compile('^Добави ')).evaluate_all('(els)=>els.map(e=>e.getAttribute("aria-label"))')
 assert names and all('телевизор' in name.casefold() for name in names),names
 proof['query_only_filter_without_explicit_checkboxes']=True
 # Original grocery photos and a visible one-second green add acknowledgement.
 page.get_by_role('tab',name='Храни',exact=True).click()
 expect(page.get_by_role('img',name='прясно мляко',exact=True)).to_be_visible()
 add=page.get_by_role('button',name='Добави прясно мляко',exact=True)
 initial=add.evaluate('(e)=>getComputedStyle(e).backgroundColor');add.click()
 assert add.evaluate('(e)=>getComputedStyle(e).backgroundColor')!=initial
 page.wait_for_timeout(1200)
 assert add.evaluate('(e)=>getComputedStyle(e).backgroundColor')==initial
 proof['original_sample_gallery_and_one_second_green_add']=True
 page.wait_for_timeout(650);page.screenshot(path=str(args.output_dir/'food.png'))
 def menu(label):
  page.get_by_role('button',name='Отвори менюто',exact=True).click()
  page.get_by_role('menuitem',name=label,exact=True).click()
 menu('Настройки')
 page.wait_for_timeout(650);page.screenshot(path=str(args.output_dir/'settings.png'))
 page.get_by_role('button',name='Размер на шрифта',exact=True).click()
 for i in range(4):
  radio=page.get_by_role('radio').nth(i);radio.click()
  expect(radio).to_have_attribute('aria-checked','true')
  assert radio.bounding_box()['height']>=44
 page.wait_for_timeout(650);page.screenshot(path=str(args.output_dir/'font.png'))
 proof['all_four_font_options_work_and_keep_accessible_targets']=True
 menu('За приложението')
 page.get_by_role('button',name='Обратна връзка',exact=True).click()
 page.get_by_label('Вашето име',exact=True).fill('Демо потребител')
 page.get_by_label('Ел. поща за връзка',exact=True).fill('test@example.invalid')
 page.get_by_label('Текст на запитването',exact=True).fill('Проверка на примерния интерфейс за обратна връзка.')
 expect(page.get_by_role('button',name='Изпрати',exact=True)).to_be_enabled()
 assert page.locator('iframe[src*="captcha"]').count()==0
 page.wait_for_timeout(650);page.screenshot(path=str(args.output_dir/'feedback.png'))
 page.get_by_role('button',name='Изпрати',exact=True).click()
 expect(page.get_by_text('Съобщението е прието от пощенския сървър.',exact=True)).to_be_visible()
 evidence=page.request.get(args.api_url+'/__simulation/feedback').json()
 assert evidence['is_simulation'] and evidence['messages'][-1]['recipient']=='ivo77@duck.com'
 proof['mock_feedback_fixed_recipient_optional_phone_and_no_captcha']=True
 result=page.request.post(args.api_url+'/__simulation/feedback-mode',data={'mode':'failure'});assert result.ok
 page.get_by_label('Текст на запитването',exact=True).fill('Проверка на отказ при изпращане през примерния доставчик.')
 page.get_by_role('button',name='Изпрати',exact=True).click()
 expect(page.get_by_text('Изпращането на съобщения временно не е достъпно.',exact=True)).to_be_visible()
 proof['feedback_failure_never_reports_success']=True
 page.request.post(args.api_url+'/__simulation/feedback-mode',data={'mode':'unavailable'})
 page.get_by_role('button',name='Назад',exact=True).click()
 page.get_by_role('button',name='Обратна връзка',exact=True).click()
 expect(page.get_by_role('button',name='Изпрати',exact=True)).to_be_disabled()
 proof['feedback_unconfigured_state_disables_sending']=True
 page.request.post(args.api_url+'/__simulation/feedback-mode',data={'mode':'available'})
 assert not errors,errors
 proof['javascript_errors']=errors
 browser.close()
(args.output_dir/'proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2))
print(json.dumps(proof,ensure_ascii=False))
