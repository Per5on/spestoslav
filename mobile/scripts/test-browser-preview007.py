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
 photo_notice='Снимките са илюстративни. Действителният продукт или опаковката може да изглеждат различно.'
 expect(page.get_by_test_id("catalog-footer").get_by_text("Снимките са илюстративни.",exact=True)).to_be_visible()
 page.get_by_test_id('thumbnail-loaded-demo-milk').click()
 viewer=page.get_by_test_id('thumbnail-viewer')
 expect(viewer.get_by_text(photo_notice,exact=True)).to_be_visible()
 expect(viewer.get_by_role('img',name='прясно мляко',exact=True)).to_be_visible()
 assert viewer.get_by_role('img').bounding_box()['height']>250
 page.screenshot(path=str(args.output_dir/'thumbnail-zoom.png'))
 viewer.get_by_role('button',name='Затвори снимката',exact=True).click()
 expect(viewer).to_have_count(0)
 proof['thumbnail_enlarges_and_closes_in_app']=True
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
 expect(page.get_by_test_id("catalog-footer").get_by_text("Снимките са илюстративни.",exact=True)).to_be_visible()
 toolbar=page.get_by_test_id('catalog-toolbar')
 page.get_by_role('button',name='Отвори менюто',exact=True).click()
 page.get_by_role('menuitem',name='Търговски обекти',exact=True).click()
 directory=page.get_by_test_id('merchant-directory')
 for name in ['Зора','Technopolis','Technomarket','Techmart','Вали','Ardes','Jar Computers']:
  expect(directory.get_by_text(name,exact=False)).to_be_visible(timeout=15000)
 expect(directory.get_by_role('heading',name='София',exact=True)).to_have_count(3)
 proof['seven_requested_chains_with_recorded_addresses']=True
 page.screenshot(path=str(args.output_dir/'merchant-directory.png'))
 route_pattern='**/api/v1/merchant-directory?*'
 page.route(route_pattern,lambda route:route.fulfill(status=404,json={'detail':'Not Found'}))
 directory.get_by_role('button',name='Обнови',exact=True).click()
 expect(directory.get_by_text('Запазен списък с обекти',exact=False)).to_be_visible()
 for entry in (
  'Kaufland · ул. Краков 2Б', 'Lidl · ул. Д-р Атанас Москов 18',
  'BILLA · Бул. Възкресение 66', 'Fantastico · бул. "Мадрид" №8',
  'T MARKET · ул. Марагидик 17', 'METRO · ул. Костиевска №1',
 ):
  expect(directory.get_by_text(entry,exact=True)).to_have_count(1)
 proof['snapshot_has_verified_addresses_from_six_grocery_chains']=True
 tech_section = directory.get_by_role('heading', name='Техника', exact=True).locator('..')
 for entry in (
  'Techmart · Магазин Божурище · бул. "Сливница" 437',
  'Зора · бул. Цар Освободител 37А',
  'Jar Computers · JAR Computers Благоевград · бул. Джеймс Баучер 10',
  'Technomarket · ТЕХНОМАРКЕТ АСЕНОВГРАД · бул. България 68',
  'Ardes · ж.к. Братя Миладинови, бл. 91',
  'Technopolis · Технополис Благоевград · ул. Св. Димитър Солунски 5',
  'Вали · бул. Христо Смирненски 239',
 ):
  expect(tech_section.get_by_text(entry, exact=True)).to_have_count(1)
 proof['saved_directory_displays_all_seven_technology_retailers']=True
 fuel_section = directory.get_by_role('heading', name='Горива', exact=True).locator('..')
 for entry in (
  'Rompetrol · Rompetrol София 7 · бул. Ботевградско шосе №231',
  'LUKOIL · Lukoil Б001 · Аерогара София - Терминал 1',
  'Petrol · Petrol 7129 София: КАТ · бул. Драган Цанков (срещу КАТ)',
  'Shell · Shell 2008 София Симеоново · Околовръстен път, km 46+717',
  'EKO · Eko 1192 София – Александър Малинов · бул. Александър Малинов №37',
  'OMV · OMV Младост 1А · бул. Александър Малинов',
 ):
  expect(fuel_section.get_by_text(entry, exact=True)).to_have_count(1)
 proof['saved_directory_displays_all_six_fuel_chains']=True
 page.screenshot(path=str(args.output_dir/'merchant-snapshot.png'))
 page.unroute(route_pattern)
 directory.get_by_role('button',name='Обнови',exact=True).click()
 expect(directory.get_by_text('Запазен списък с обекти',exact=False)).to_have_count(0)
 proof['directory_404_uses_dated_snapshot_and_recovers']=True
 page.get_by_role('tab',name='Техника',exact=True).click()
 page.get_by_label('Търси населено място…',exact=True).fill('Sofia')
 page.get_by_text('София',exact=True).first.click()
 page.get_by_role('tab',name='Горива',exact=True).click()
 for index,name in enumerate(['Бензин 95','Бензин 98+','Дизел','Дизел +','Автогаз']):
  page.get_by_role('radio',name=name,exact=True).click()
  expect(page.get_by_text(f'{1.48+index*.1:.2f} €/L',exact=True)).to_be_visible(timeout=10000)
 expect(page.get_by_text('Примерен обект · демонстрационен адрес',exact=True)).to_have_count(6)
 proof['six_requested_stations_and_all_five_price_filters']=True
 page.wait_for_timeout(650);page.screenshot(path=str(args.output_dir/'fuel.png'))
 page.get_by_role('tab',name='Техника',exact=True).click()
 expect(page.get_by_test_id('thumbnail-loaded-demo-laptop')).to_be_visible(timeout=20000)
 expect(page.get_by_test_id('thumbnail-loaded-demo-laptop')).to_have_accessible_name(re.compile('Символично изображение$'))
 search=page.get_by_label('Търси продукт…',exact=True)
 search.fill('Лаптоп')
 suggestions=page.get_by_test_id('product-suggestions')
 suggestions.get_by_role('button',name='Лаптоп (примерна снимка)',exact=True).click()
 expect(suggestions).to_have_count(0)
 expect(page.get_by_role('button',name=re.compile('^Добави '))).to_have_count(1)
 expect(page.get_by_role('button',name='Добави Лаптоп (примерна снимка)',exact=True)).to_be_visible()
 expect(page.get_by_role('button',name=re.compile('^(Приложи|Изчисти)'))).to_have_count(0)
 search.fill('Смартфон')
 suggestions.get_by_role('button',name='Смартфон (примерна снимка)',exact=True).click()
 expect(page.get_by_role('button',name=re.compile('^Добави '))).to_have_count(1)
 expect(page.get_by_role('button',name='Добави Смартфон (примерна снимка)',exact=True)).to_be_visible()
 assert page.evaluate("() => JSON.parse(localStorage.getItem('spestovnik-preview-001')).basket") == []
 proof['search_selection_filters_without_adding_or_extra_controls']=True
 search.fill('телевизор')
 search.press('Enter')
 expect(suggestions).to_have_count(0)
 names=page.get_by_role('button',name=re.compile('^Добави ')).evaluate_all('(els)=>els.map(e=>e.getAttribute("aria-label"))')
 assert names and all('телевизор' in name.casefold() for name in names),names
 page.screenshot(path=str(args.output_dir/'technology.png'))
 search.fill('')
 expect(page.get_by_test_id('thumbnail-loaded-demo-laptop')).to_be_visible()
 proof['enter_filters_catalogue_and_empty_input_restores_it']=True
 # The representative images are local assets and are tied to catalogue IDs.
 def verify_catalogue_image(category, tab, code, query):
  page.get_by_role('tab',name=tab,exact=True).click()
  snapshot=page.request.get(args.api_url + '/api/v1/catalog/' + category).json()['products']
  product=next(row for row in snapshot if row['source_product_code']==code)
  search=page.get_by_label('Търси продукт…',exact=True)
  search.fill(query)
  search.press('Enter')
  img=page.get_by_test_id('thumbnail-loaded-'+product['id'])
  expect(img).to_be_visible(timeout=20000)
  expect(img).to_have_accessible_name(re.compile('Примерна снимка$'))
 page.get_by_role('tab',name='Храни',exact=True).click()
 search=page.get_by_label('Търси продукт…',exact=True)
 search.fill('банани')
 search.press('Enter')
 banana=page.get_by_role('button',name='Добави Банани · 1 кг',exact=True)
 expect(banana).to_have_count(1)
 expect(page.get_by_role('img',name='Банани · 1 кг · Примерна снимка',exact=True)).to_be_visible(timeout=20000)
 search.fill('81590')
 search.press('Enter')
 expect(banana).to_be_visible()
 page.screenshot(path=str(args.output_dir/'banana-grouped.png'))
 proof['grocery_choices_group_matching_packages_and_keep_search_aliases']=True
 search.fill('домати')
 search.press('Enter')
 tomato=page.get_by_role('img',name=re.compile('ДОМАТИ.*Символично изображение',re.I)).first
 expect(tomato).to_have_attribute('src',re.compile('tomato'))
 proof['tomatoes_use_tomato_artwork']=True
 page.screenshot(path=str(args.output_dir/"tomato-thumbnail.png"))
 verify_catalogue_image('technology','Техника','43832','SM-A176B GALAXY A17 5G 4/128GB Black')
 proof['product_matched_webp_pilot']=True
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
