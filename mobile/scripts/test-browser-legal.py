"""Legal documents and feedback privacy links: readable and non-destructive."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=False)
proof={};errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=2);page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8775',wait_until='domcontentloaded')
 def menu(label):
  page.get_by_role('button',name='Отвори менюто',exact=True).click(timeout=30000);page.get_by_role('menuitem',name=label,exact=True).click()
 menu('Настройки');page.wait_for_timeout(700);page.screenshot(path=str(args.output_dir/'settings-with-policies.png'))
 page.get_by_role('button',name='Общи условия',exact=True).click();expect(page.get_by_test_id('legal-terms')).to_be_visible()
 expect(page.get_by_text('3. Примерни снимки и симулации',exact=True)).to_be_visible()
 assert 'Ivaylo Yovchev' in page.get_by_test_id('legal-terms').inner_text()
 assert 'Политика за поверителност' in page.get_by_test_id('legal-terms').inner_text()
 page.get_by_role('button',name='English',exact=True).click();expect(page.get_by_text('3. Illustrative photographs and simulations',exact=True)).to_be_visible()
 page.get_by_role('button',name='Назад',exact=True).click();expect(page.get_by_role('button',name='Политика за поверителност',exact=True)).to_be_visible()
 page.get_by_role('button',name='Политика за поверителност',exact=True).click();expect(page.get_by_test_id('legal-privacy')).to_be_visible();page.wait_for_timeout(700);page.screenshot(path=str(args.output_dir/'privacy.png'))
 proof['settings_terms_include_privacy_and_bilingual_illustration_clause']=True
 menu('За приложението');page.get_by_role('button',name='Обратна връзка',exact=True).click()
 page.get_by_label('Вашето име',exact=True).fill('Демо потребител')
 page.get_by_label('Текст на запитването',exact=True).fill('Тази чернова трябва да се запази при преглед на политиката.')
 page.get_by_role('link',name='Политика за поверителност',exact=True).click()
 expect(page.get_by_test_id('legal-privacy')).to_be_visible()
 page.get_by_role('button',name='Затвори',exact=True).click();expect(page.get_by_test_id('legal-privacy')).not_to_be_visible()
 expect(page.get_by_label('Вашето име',exact=True)).to_have_value('Демо потребител')
 expect(page.get_by_label('Текст на запитването',exact=True)).to_have_value('Тази чернова трябва да се запази при преглед на политиката.')
 proof['privacy_link_preserves_private_unsent_form_draft']=True
 assert not errors,errors;proof['javascript_errors']=errors;browser.close()
(args.output_dir/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
