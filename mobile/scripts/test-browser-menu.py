import os,json
from pathlib import Path

from playwright.sync_api import sync_playwright,expect
import argparse,tempfile
from datetime import datetime
parser=argparse.ArgumentParser(description="Local browser verification; no Android build or live data writes.")
parser.add_argument('--base-url',default='http://127.0.0.1:8775')
parser.add_argument('--api-url',default='http://127.0.0.1:8774')
parser.add_argument('--fixtures',type=Path,default=Path(tempfile.gettempdir())/'spestovnik-simulation')
parser.add_argument('--output-dir',type=Path,default=Path(tempfile.gettempdir())/('spestovnik-menu-'+datetime.now().strftime('%Y%m%d-%H%M%S')))
args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=False)

errors=[];proof={}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=os.getenv('PLAYWRIGHT_CHROMIUM_EXECUTABLE'),args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844});page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(args.base_url,wait_until='domcontentloaded')
 refresh = page.get_by_role('button', name='Обнови цени', exact=True)
 refresh.wait_for(timeout=60000)
 refresh.focus()
 assert refresh.evaluate("(el) => getComputedStyle(el).outlineWidth") == "0px"
 assert refresh.evaluate("(el) => getComputedStyle(el).borderTopWidth") == "0px"
 assert refresh.evaluate("(el) => getComputedStyle(el).backgroundColor") == "rgb(219, 234, 211)"
 page.screenshot(path=str(args.output_dir/'catalogue-bg.png'))
 page.get_by_role('button',name='Отвори менюто',exact=True).click(timeout=60000)
 labels=page.get_by_role('menuitem').evaluate_all('(els)=>els.map(e=>e.getAttribute("aria-label"))')
 assert labels==['Търговски обекти','Сканирай','Касови бележки','Вход','Настройки','За приложението'],labels
 page.screenshot(path=str(args.output_dir/'preview005-issue8-menu-bg.png'));page.get_by_role('menuitem',name='За приложението',exact=True).click()
 expect(page.get_by_test_id('about-screen')).to_be_visible();expect(page.get_by_text('© 2026 Vimp. All rights reserved.',exact=True)).to_be_visible()
 about = page.get_by_test_id('about-screen')
 expect(about.get_by_role('link')).to_have_count(0)
 assert 'Лаптоп' not in about.inner_text() and 'https://' not in about.inner_text()
 expect(about.get_by_role('button')).to_have_count(2)
 page.screenshot(path=str(args.output_dir/'about-bg.png'))
 about.get_by_role('button', name='Трети страни', exact=True).click()
 credits = page.get_by_test_id('third-parties-screen')
 expect(credits).to_be_visible()
 expect(credits.get_by_role('button')).to_have_count(4)
 for label, source in [
   ('Данни и цени', 'KARAI Fuel Index'),
   ('Търговски обекти и адреси', 'Fuelo · EKO, LUKOIL, OMV, Rompetrol, Shell, Petrol'),
   ('Снимки и икони', 'Samsung Galaxy A17 5G'),
   ('Софтуер и услуги', 'Expo'),
 ]:
  section = credits.get_by_role('button', name=label, exact=True)
  section.click()
  expect(section).to_have_attribute('aria-expanded', 'true')
  expect(credits.get_by_role('link', name=source, exact=True)).to_be_attached()
  if label == 'Софтуер и услуги':
   expect(credits.get_by_role('link', name='Tesseract OCR', exact=True)).to_be_attached()
  if label == 'Данни и цени':
   expect(credits.get_by_role('link', name='CC BY 4.0', exact=True)).to_be_visible()
   page.screenshot(path=str(args.output_dir/'third-parties-bg.png'))
  section.click()
  expect(credits.get_by_role('link')).to_have_count(0)
 page.get_by_role('button', name='Назад', exact=True).click()
 expect(about).to_be_visible()
 proof['credits_nested_in_about_and_back_navigation'] = True
 feedback = page.get_by_role('button',name='Обратна връзка',exact=True)
 light_green = feedback.evaluate("(el) => getComputedStyle(el).backgroundColor")
 feedback.click();expect(page.get_by_test_id('about-screen')).not_to_be_visible();page.get_by_role('button',name='Назад',exact=True).click();expect(page.get_by_test_id('about-screen')).to_be_visible();proof['feedback_nested_in_about_and_back_navigation']=True
 assert not page.get_by_text('Профил',exact=True).count();proof['bulgarian_menu_order_and_direct_about']=True
 page.get_by_role('button',name='Отвори менюто',exact=True).click();page.get_by_role('menuitem',name='Настройки',exact=True).click()
 font_choice = page.get_by_role('button',name='Размер на шрифта',exact=True)
 assert font_choice.evaluate("(el) => getComputedStyle(el).backgroundColor") == light_green
 assert font_choice.evaluate("(el) => getComputedStyle(el).borderTopWidth") == "0px"
 assert font_choice.evaluate("(el) => parseFloat(getComputedStyle(el).borderTopLeftRadius)") >= 12
 page.screenshot(path=str(args.output_dir/'settings-bg.png'))
 proof['borderless_refresh_and_settings_buttons'] = True
 font_choice.click();page.get_by_role('radio').nth(2).click();page.get_by_role('button',name='Назад',exact=True).click();expect(page.get_by_role('button',name='Език',exact=True)).to_be_visible();proof['nested_settings_and_back_navigation']=True
 page.get_by_role('button',name='Език',exact=True).click();page.get_by_role('radio',name='English',exact=True).click();page.get_by_role('button',name='Open menu',exact=True).click()
 labels=page.get_by_role('menuitem').evaluate_all('(els)=>els.map(e=>e.getAttribute("aria-label"))')
 assert labels==['Merchant directory','Scan','Receipts','Sign in','Settings','About'],labels
 page.get_by_role('menuitem',name='About',exact=True).click();expect(page.get_by_role('menu')).not_to_be_visible();expect(page.get_by_text('About',exact=True)).to_be_visible();expect(page.get_by_text('© 2026 Vimp. All rights reserved.',exact=True)).to_be_visible();page.screenshot(path=str(args.output_dir/'preview005-issue8-about-en.png'))
 page.get_by_role('button',name='Feedback',exact=True).click();page.get_by_role('button',name='Back',exact=True).click();expect(page.get_by_test_id('about-screen')).to_be_visible()
 page.reload();page.get_by_role('button',name='Open menu',exact=True).wait_for(timeout=20000);page.get_by_role('button',name='Open menu',exact=True).click();page.get_by_role('menuitem',name='Settings',exact=True).click();page.get_by_role('button',name='Font size',exact=True).click();expect(page.get_by_role('radio').nth(2)).to_have_attribute('aria-checked','true');proof['english_and_preferences_persist']=True
 assert not errors,errors
 proof['javascript_errors']=errors;browser.close()
(args.output_dir/'preview005-issue8-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
