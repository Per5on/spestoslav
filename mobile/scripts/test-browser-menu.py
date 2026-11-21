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
 browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844});page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(args.base_url,wait_until='domcontentloaded')
 refresh = page.get_by_role('button', name='Обнови', exact=True)
 refresh.wait_for(timeout=60000)
 refresh.focus()
 assert refresh.evaluate("(el) => getComputedStyle(el).outlineWidth") == "0px"
 assert refresh.evaluate("(el) => getComputedStyle(el).borderTopWidth") == "0px"
 assert refresh.evaluate("(el) => getComputedStyle(el).backgroundColor") == "rgb(219, 234, 211)"
 page.screenshot(path=str(args.output_dir/'catalogue-bg.png'))
 page.get_by_role('button',name='Отвори менюто',exact=True).click(timeout=60000)
 labels=page.get_by_role('menuitem').evaluate_all('(els)=>els.map(e=>e.getAttribute("aria-label"))')
 assert labels==['Търговски обекти','Сканирай','Касови бележки','Вход','Настройки','За приложението'],labels
 # Simulate verified-directory API responses locally: first a branch, then a failure.
 # This tests refresh clearing stale content without contacting the live API.
 directory_calls=[0]
 def directory_response(route):
  directory_calls[0]+=1
  if directory_calls[0]==1:
   route.fulfill(status=200,content_type='application/json',body=json.dumps([{'id':'fixture-branch-1','category_code':'groceries','retailer_code':'fixture','retailer_name':'Fixture Retailer','locality_id':'fixture-town','locality_name':'Fixture Town','municipality':None,'region':None,'branch_name':None,'address':'Fixture Address'}]))
  elif directory_calls[0]==2:
   route.fulfill(status=503,content_type='application/json',body='{"error":"simulated failure"}')
  elif directory_calls[0]==3:
   route.fulfill(status=200,content_type='application/json',body=json.dumps([{'id':'fixture-branch-2','category_code':'groceries','retailer_code':'fixture-recovered','retailer_name':'Recovered Fixture Retailer','locality_id':'fixture-new-town','locality_name':'Recovered Fixture Town','municipality':None,'region':None,'branch_name':None,'address':'Recovered Fixture Address'}]))
  else:
   route.fulfill(status=200,content_type='application/json',body='[]')

 page.route('**/api/v1/merchant-directory?*',directory_response)
 page.get_by_role('menuitem',name='Търговски обекти',exact=True).click()
 directory=page.get_by_test_id('merchant-directory')
 expect(directory).to_be_visible()
 expect(page.get_by_role('menu')).not_to_be_visible()
 locality=directory.get_by_role('button',name='Fixture Town (1)')
 expect(locality).to_have_attribute('aria-expanded','false')
 locality.click()
 expect(locality).to_have_attribute('aria-expanded','true')
 expect(directory.get_by_text('Fixture Retailer')).to_be_visible()
 assert directory_calls[0]==1,directory_calls
 directory.get_by_role('button',name='Обнови',exact=True).click()
 expect(directory.get_by_role('alert')).to_be_visible()
 expect(directory.get_by_text('Fixture Retailer')).to_have_count(0)
 expect(directory.get_by_text('Fixture Address',exact=True)).to_have_count(0)
 expect(directory.get_by_text('Fixture Town (1)',exact=True)).to_have_count(0)
 assert directory_calls[0]==2,directory_calls
 proof['merchant_directory_refresh_discards_stale_rows_on_failure']=True
 # A third refresh must recover cleanly, without resurrecting the first response.
 directory.get_by_role('button',name='Обнови',exact=True).click()
 expect(directory.get_by_role('alert')).to_have_count(0)
 expect(directory.get_by_role('button',name='Recovered Fixture Town (1)')).to_be_visible()
 expect(directory.get_by_text('Fixture Town (1)',exact=True)).to_have_count(0)
 recovered_locality=directory.get_by_role('button',name='Recovered Fixture Town (1)')
 expect(recovered_locality).to_have_attribute('aria-expanded','false')
 # Recovery must not implicitly expand a previously expanded locality.
 expect(directory.get_by_text('Recovered Fixture Retailer',exact=True)).to_have_count(0)
 expect(directory.get_by_text('Recovered Fixture Address',exact=True)).to_have_count(0)
 recovered_locality.click()
 expect(recovered_locality).to_have_attribute('aria-expanded','true')
 expect(directory.get_by_text('Recovered Fixture Retailer')).to_be_visible()
 recovered_locality.click()
 expect(recovered_locality).to_have_attribute('aria-expanded','false')
 expect(directory.get_by_text('Recovered Fixture Retailer')).to_have_count(0)
 recovered_locality.click()
 expect(recovered_locality).to_have_attribute('aria-expanded','true')
 expect(directory.get_by_text('Recovered Fixture Retailer')).to_be_visible()
 expect(directory.get_by_text('Recovered Fixture Address',exact=True)).to_be_visible()
 expect(directory.get_by_text('Fixture Address',exact=True)).to_have_count(0)
 proof['merchant_directory_locality_accessibility_and_toggle']=True
 expect(directory.get_by_text('Fixture Retailer',exact=True)).to_have_count(0)
 assert directory_calls[0]==3,directory_calls
 proof['merchant_directory_recovers_after_refresh_failure']=True
 # A successful empty response must clear the recovered locality and its address.
 directory.get_by_role('button',name='Обнови',exact=True).click()
 expect(directory.get_by_role('alert')).to_have_count(0)
 expect(directory.get_by_role('button',name='Recovered Fixture Town (1)')).to_have_count(0)
 expect(directory.get_by_text('Recovered Fixture Retailer',exact=True)).to_have_count(0)
 expect(directory.get_by_text('Recovered Fixture Address',exact=True)).to_have_count(0)
 assert directory_calls[0]==4,directory_calls
 proof['merchant_directory_empty_refresh_discards_recovered_rows']=True
 page.unroute('**/api/v1/merchant-directory?*',directory_response)
 page.get_by_role('button',name='Назад',exact=True).click()
 expect(page.get_by_test_id('catalog-toolbar')).to_be_visible()
 page.get_by_role('button',name='Отвори менюто',exact=True).click()
 page.screenshot(path=str(args.output_dir/'preview005-issue8-menu-bg.png'));page.get_by_role('menuitem',name='За приложението',exact=True).click()
 expect(page.get_by_test_id('about-screen')).to_be_visible();expect(page.get_by_text('© 2026 Vimp. All rights reserved.',exact=True)).to_be_visible()
 about = page.get_by_test_id('about-screen')
 expect(about.get_by_role('link')).to_have_count(0)
 assert 'Лаптоп' not in about.inner_text() and 'https://' not in about.inner_text()
 expect(about.get_by_role('button')).to_have_count(1)
 page.screenshot(path=str(args.output_dir/'about-bg.png'))
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
