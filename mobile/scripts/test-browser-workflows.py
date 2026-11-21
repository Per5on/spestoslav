import os,json
from pathlib import Path

from playwright.sync_api import sync_playwright,expect
import argparse,tempfile
from datetime import datetime
parser=argparse.ArgumentParser(description="Local browser verification; no Android build or live data writes.")
parser.add_argument('--base-url',default='http://127.0.0.1:8775')
parser.add_argument('--api-url',default='http://127.0.0.1:8774')
parser.add_argument('--fixtures',type=Path,default=Path(tempfile.gettempdir())/'spestovnik-simulation')
parser.add_argument('--output-dir',type=Path,default=Path(tempfile.gettempdir())/('spestovnik-workflows-'+datetime.now().strftime('%Y%m%d-%H%M%S')))
args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=False)

root=args.fixtures;proof={};errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--use-file-for-fake-video-capture='+str(root/'simulation-camera.y4m')])
 context=browser.new_context(viewport={'width':390,'height':844},permissions=['camera']);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));calls=[];page.on('request',lambda r:calls.append(r.url))
 page.goto(args.base_url,wait_until='domcontentloaded')
 milk=page.get_by_role('button',name='Добави SIM Мляко 1 L',exact=True);milk.wait_for(timeout=120000)
 page.get_by_label('Търси населено място…',exact=True).fill('Sofia');page.get_by_text('София',exact=True).click()
 milk.click();milk.click();page.get_by_role('button',name='Добави SIM Олио 1 L',exact=True).click()
 page.get_by_role('tab',name='Сравни цените',exact=True).click();page.get_by_role('button',name='Сравни цени',exact=True).click();expect(page.get_by_text('5.50 €',exact=False)).to_be_visible(timeout=15000)
 proof['complete_basket_comparison']=True
 def menu(name):
  page.get_by_role('button',name='Отвори менюто',exact=True).click();page.get_by_role('menuitem',name=name,exact=True).click()
 # Existing overflow items use menuitem accessibility roles.
 menu('Сканирай');page.get_by_role('button',name='Отвори камерата',exact=True).click();expect(page.get_by_label('Търсене по баркод',exact=True)).to_have_value('4006381333931',timeout=30000);expect(page.get_by_text('SIM Мляко 1 L',exact=True)).to_be_visible();proof['live_camera_decoded_synthetic_ean13']=True
 page.get_by_label('Търсене по баркод',exact=True).fill('')
 with page.expect_file_chooser() as picker:page.get_by_role('button',name='Баркод от снимка',exact=True).click()
 picker.value.set_files(root/'simulation-ean13.png');expect(page.get_by_label('Търсене по баркод',exact=True)).to_have_value('4006381333931',timeout=30000);proof['image_decoding']=True
 menu('Вход');page.get_by_label('Имейл',exact=True).fill('alice@example.invalid');page.get_by_label('Парола (поне 8 знака)',exact=True).fill('simulation-password');page.get_by_role('button',name='Вход',exact=True).click();expect(page.get_by_text('alice@example.invalid',exact=True)).to_be_visible(timeout=15000)
 menu('Сканирай');page.get_by_label('Търсене по баркод',exact=True).fill('1234567890128');page.get_by_role('button',name='Намери продукт',exact=True).click();page.get_by_role('button',name='Заяви разпознаване',exact=True).click(timeout=10000);expect(page.get_by_text('Заявката е изпратена за проверка. Не е добавен непроверен продукт.',exact=True)).to_be_visible();proof['unknown_barcode_review_request']=True
 menu('Касови бележки')
 with page.expect_file_chooser() as picker:page.get_by_role('button',name='Избери снимка',exact=True).click()
 picker.value.set_files(root/'simulation-receipt.png');page.get_by_role('button',name='Изпрати лично',exact=True).click();expect(page.get_by_text('В опашката за обработка',exact=True).first).to_be_visible(timeout=15000)
 result=page.request.post(args.api_url+'/__simulation/ocr');assert result.json()['processed'] is True
 page.get_by_role('button',name='Обнови',exact=True).click();expect(page.get_by_text('За проверка',exact=True).first).to_be_visible(timeout=15000);page.screenshot(path=str(args.output_dir/'preview005-step1-receipts.png'),full_page=True);proof['private_upload_and_real_bulgarian_ocr']=True
 receipt_line=page.get_by_text('МЛЯКО 2.20 EUR',exact=True).locator('..')
 receipt_line.get_by_role('button',name='Провери реда',exact=True).click()
 page.get_by_label('Избери точния продукт',exact=True).fill('SIM Мляко')
 page.get_by_role('button',name='SIM Мляко 1 L',exact=True).click()
 page.get_by_role('radio',name='Симулация A · Тестова улица A',exact=True).click()
 expect(page.get_by_label('Единична цена в EUR',exact=True)).to_have_value('')
 page.get_by_label('Единична цена в EUR',exact=True).fill('1.10')
 page.get_by_role('checkbox',name='Потвърждавам продукта, магазина и единичната цена.',exact=False).click()
 page.get_by_role('button',name='Изпрати за проверка',exact=True).click()
 expect(page.get_by_text('Изпратено за проверка. Цената още не е публикувана.',exact=True).first).to_be_visible()
 approved=page.request.post(args.api_url+'/__simulation/approve');assert approved.status==200,approved.text()
 page.get_by_role('button',name='Обнови',exact=True).click();expect(page.get_by_text('Проверена цена',exact=True)).to_be_visible()
 proof['explicit_unit_price_confirmation_and_moderation']=True
 page.once('dialog',lambda d:d.accept());page.get_by_role('button',name='Изтрий бележката',exact=True).click();expect(page.get_by_text('Няма запазени бележки.',exact=True)).to_be_visible(timeout=15000);proof['receipt_deletion']=True
 stored=page.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage)))')
 assert 'simulation-jwt-' not in stored and 'alice@example.invalid' not in stored
 proof['private_session_not_in_public_storage']=True
 page.get_by_role('tab',name='Храни',exact=True).click();before=len([u for u in calls if '/catalog/groceries' in u]);page.reload();page.get_by_role('button',name='Добави SIM Мляко 1 L',exact=True).wait_for(timeout=20000);after=len([u for u in calls if '/catalog/groceries' in u]);assert after==before;proof['catalogue_restores_without_refetch']=True
 route=page.request.get(args.api_url+'/__simulation/route').json();assert route['is_simulation'] and route['distance_km']==4 and not route['real_directions_available'];proof['free_route_mock_matrix']=True
 page.screenshot(path=str(args.output_dir/'preview005-step1-catalogue.png'),full_page=False)
 assert not errors,errors
 proof['javascript_errors']=errors
 denied_context=browser.new_context(viewport={"width":390,"height":844})
 denied=denied_context.new_page();denied.on("pageerror",lambda e:errors.append(str(e)))
 denied.add_init_script("navigator.mediaDevices.getUserMedia=()=>Promise.reject(new DOMException('Simulation denial','NotAllowedError'))")
 denied.goto(args.base_url,wait_until='domcontentloaded');denied.get_by_role('button',name='Отвори менюто',exact=True).click(timeout=30000);denied.get_by_role('menuitem',name='Сканирай',exact=True).click();denied.get_by_role('button',name='Отвори камерата',exact=True).click()
 expect(denied.get_by_text('Камерата е забранена. Разрешете достъп в настройките или въведете кода.',exact=True)).to_be_visible()
 denied.get_by_label('Търсене по баркод',exact=True).fill('4006381333931');denied.get_by_role('button',name='Намери продукт',exact=True).click();expect(denied.get_by_text('SIM Мляко 1 L',exact=True)).to_be_visible()
 proof['denied_camera_manual_fallback']=True
 assert not errors,errors
 browser.close()
(args.output_dir/'preview005-step1-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
