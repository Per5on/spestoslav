import os,json
from pathlib import Path

from playwright.sync_api import sync_playwright,expect
import argparse,tempfile
from datetime import datetime
parser=argparse.ArgumentParser(description="Local browser verification; no Android build or live data writes.")
parser.add_argument('--base-url',default='http://127.0.0.1:8775')
parser.add_argument('--api-url',default='http://127.0.0.1:8774')
parser.add_argument('--fixtures',type=Path,default=Path(tempfile.gettempdir())/'spestovnik-simulation')
parser.add_argument('--output-dir',type=Path,default=Path(tempfile.gettempdir())/('spestovnik-toolbars-'+datetime.now().strftime('%Y%m%d-%H%M%S')))
args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=False)

errors=[];proof={}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(args.base_url,wait_until='domcontentloaded')
 toolbar=page.get_by_test_id('catalog-toolbar');toolbar.wait_for(timeout=60000)
 assert page.get_by_role('tab').evaluate_all('(els)=>els.map(e=>e.getAttribute("aria-label"))')==['Храни','Техника','Горива','Сравни цените']
 expect(toolbar.get_by_role('button')).to_have_count(1,timeout=15000)
 assert toolbar.get_by_role('button').evaluate_all('(els)=>els.map(e=>e.textContent)')==['Обнови']
 def geometry(fuel=False):
  toolbar.wait_for(state="visible",timeout=20000)
  expect(toolbar.get_by_role("button")).to_have_count(3 if fuel else 1)
  buttons=toolbar.get_by_role('button')
  rects=buttons.evaluate_all('(els)=>els.map(e=>e.getBoundingClientRect().toJSON())')
  if fuel: assert abs(rects[0]['width']-rects[1]['width'])<1,rects
  assert max(r['y'] for r in rects)-min(r['y'] for r in rects)<1,rects
  if fuel: assert rects[0]['x']<rects[1]['x']<rects[2]['x']
  padding=buttons.nth(2 if fuel else 0).evaluate('(e)=>parseFloat(getComputedStyle(e).paddingLeft)+parseFloat(getComputedStyle(e).paddingRight)');assert abs(padding-14)<.01,padding
  for i in range(3 if fuel else 1):
   box=buttons.nth(i).evaluate('(e)=>{let t=e.querySelector("[dir=auto]");return {font:parseFloat(getComputedStyle(t).fontSize),scroll:t.scrollWidth,width:t.clientWidth,height:e.getBoundingClientRect().height};}')
   assert box['font']>=12,box
   assert box['scroll']<=box['width']+1,(page.evaluate('localStorage.getItem("spestovnik-preferences")'),buttons.nth(i).inner_text(),box)
   assert box['height']>=44,box
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 geometry()
 # When the fixture contains more than four groups, overflow must expose
 # an accessible name and reflect its expanded/collapsed state.
 group_choices=page.get_by_test_id('category-group-choices')
 if group_choices.count():
  more=group_choices.get_by_role('button',name='Покажи всички групи')
  if more.count():
   assert more.get_attribute('aria-expanded')=='false'
   more.click()
   less=group_choices.get_by_role('button',name='Скрий допълнителните групи')
   expect(less).to_be_visible()
   assert less.get_attribute('aria-expanded')=='true'
   less.click()
   expect(more).to_be_visible()
   assert more.get_attribute('aria-expanded')=='false'
 proof['group_overflow_accessibility_checked_if_fixture_supports_it']=True
 padding=page.get_by_test_id('app-header').evaluate('(e)=>parseFloat(getComputedStyle(e).paddingTop)');assert padding==10,padding;proof['header_padding_reduced_15_to_10']=True
 page.get_by_role('tab',name='Техника',exact=True).click();geometry();assert toolbar.get_by_role('button').count()==1
 page.get_by_role('tab',name='Горива',exact=True).click();geometry(fuel=True)
 assert toolbar.get_by_role('button').evaluate_all('(els)=>els.map(e=>e.textContent)')==['Бензиностанции','Гориво','Обнови']
 # The compact Fuel selector must toggle predictably and Stations must dismiss it.
 toolbar.get_by_role('button',name='Гориво',exact=True).click()
 expect(page.get_by_test_id('fuel-type-menu')).to_be_visible()
 assert toolbar.get_by_role('button',name='Гориво',exact=True).get_attribute('aria-expanded')=='true'
 toolbar.get_by_role('button',name='Гориво',exact=True).click()
 expect(page.get_by_test_id('fuel-type-menu')).not_to_be_visible()
 assert toolbar.get_by_role('button',name='Гориво',exact=True).get_attribute('aria-expanded')=='false'
 toolbar.get_by_role('button',name='Гориво',exact=True).click()
 expect(page.get_by_test_id('fuel-type-menu')).to_be_visible()
 toolbar.get_by_role('button',name='Бензиностанции',exact=True).click()
 expect(page.get_by_test_id('fuel-type-menu')).not_to_be_visible()
 assert toolbar.get_by_role('button',name='Гориво',exact=True).get_attribute('aria-expanded')=='false'
 toolbar.get_by_role('button',name='Гориво',exact=True).click()
 expect(page.get_by_test_id('fuel-type-menu')).to_be_visible()
 proof['fuel_selector_toggle_and_stations_dismissal']=True
 assert page.get_by_test_id('fuel-type-menu').get_by_role('radio').evaluate_all('(els)=>els.map(e=>e.getAttribute("aria-label"))')==['Бензин 95','Бензин 98+','Дизел','Дизел +','Автогаз']
 page.get_by_role('radio',name='Бензин 98+',exact=True).click();expect(page.get_by_test_id('fuel-type-menu')).not_to_be_visible();expect(page.get_by_text('Избрано гориво: Бензин 98+',exact=True)).to_be_visible();page.screenshot(path=str(args.output_dir/'preview005-task3-fuel.png'))
 proof['food_tech_refresh_only_and_five_fuels']=True
 for language in ['bg','en','de','es','fr','ru']:
  page.evaluate('(l)=>localStorage.setItem("spestovnik-preferences",JSON.stringify({language:l,fontScale:1.3}))',language)
  page.set_viewport_size({'width':320,'height':844});page.reload();page.get_by_role('tab').nth(0).wait_for(timeout=15000)
  for tab in [0,1,2]:
   page.get_by_role('tab').nth(tab).click();page.wait_for_timeout(180);geometry(fuel=(tab==2))
 proof['six_languages_responsive_toolbars_320px_130_percent']=True
 page.evaluate('localStorage.setItem("spestovnik-preferences",JSON.stringify({language:"bg",fontScale:1}))');page.set_viewport_size({'width':390,'height':844});page.reload();page.get_by_role('tab').nth(0).click();toolbar.wait_for();page.wait_for_timeout(300);page.screenshot(path=str(args.output_dir/'preview005-task3-food.png'))
 page.get_by_role('tab').nth(1).click();page.wait_for_timeout(300);page.screenshot(path=str(args.output_dir/'preview005-task3-technology.png'))
 assert not errors,errors;proof['javascript_errors']=errors;browser.close()
(args.output_dir/'preview005-task3-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
