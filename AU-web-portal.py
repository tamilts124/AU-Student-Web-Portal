import optparse, base64, sys, os, io
from time import sleep
import cloudscraper, tabulate
from bs4 import BeautifulSoup
from image_to_ascii import ImageToAscii

parser =optparse.OptionParser()
scraper =cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})
ascii_conv = ImageToAscii()

def help():
    parser.add_option('-r', '--regno', dest='regno', type=str, help='Register Number Of Student In Anna University [Required]')
    parser.add_option('-d', '--dob', dest='dob', type=str, help='Birth Date Of Student [Required]')

def clear():
    if sys.platform.lower().startswith('win'):os.system('cls')
    else:os.system('clear')

def find_all(option):
    if option.regno and option.dob:return True

def request_resourse(url, data={}, cookies={}, files={}, method='GET', allow_redirects=True):
    if method.upper()=='POST':response =scraper.post(url, data=data, files=files, cookies=cookies, allow_redirects=allow_redirects)
    else:response =scraper.get(url, data=data, files=files, cookies=cookies, allow_redirects=allow_redirects, cert=False)
    return response

def general_info(page):
    info ={}
    for tr in BeautifulSoup(page, 'html.parser').find_all('tr'):
        td =tr.find_all('td')
        if td[0].string and td[1].string:info[td[0].string] =td[1].string
    return info

def get_token(student_page):
    for form in BeautifulSoup(student_page, 'html.parser').find_all('form'):
        for input in form.find_all('input'):
            if input['value']:return input['value']

def get_result(result_page):
    user_info ={}
    result =[]
    for result_table in BeautifulSoup(result_page, 'html.parser').find_all('table', {'id': 'resulttable'})[1:]:
        table_rows =result_table.find_all('tr', recursive=False)
        if not user_info:
            for tr in table_rows[0].find('table').find_all('tr'):
                th =tr.find_all('th')
                user_info[th[0].string] =th[1].string
        for tr in table_rows[1:]:
            th=tr.find_all('th')
            if not [th[0].string, th[1].string, th[2].string, th[3].string] in result:
                result.append([th[0].string, th[1].string, th[2].string, th[3].string])
    return user_info, result

def web_portal(regno, dob):
    clear();print()
    print('>> Trying To Login The User Credentiales...');print()
    main_page =request_resourse('http://coe1.annauniv.edu/home')
    cookies =main_page.cookies    
    captcha_image =base64.decodebytes(main_page.text.split('base64,')[-1].split('"')[0].encode())
    token =main_page.text.split('id="pagetoken"')[-1].split('"')[1]
    ascii_conv.image_path(io.BytesIO(captcha_image))
    ascii_conv.plot()
    print();captcha =input('Captcha: ')
    student_main_page =request_resourse('http://coe1.annauniv.edu/home/students_corner.php', data={token:token, 'register_no': regno, 'dob': dob, 'security_code_student': captcha}, cookies=cookies, method='POST').text
    if 'Invalid data' in student_main_page:print('> Invalid Captcha...');sys.exit(1)
    elif 'Invalid Register number or Date of birth or Profile Not Found ...' in student_main_page:print('> Invalid Register number or Date of birth or Profile Not Found ...');sys.exit(1)
    data =general_info(student_main_page);clear();print()
    for k, v in zip(data.keys(), data.values()):print(' '+k+' : '+v)
    print();print('>> Getting Results...')
    token =get_token(student_main_page)
    student_result_page =request_resourse('http://coe1.annauniv.edu/home/students_corner.php', data={token:token, 'ExamResults': '', 'univ_reg_no': ''}, cookies=cookies, method='POST').text
    sleep(2);clear();print()
    user_info, result =get_result(student_result_page)
    for k, v in zip(user_info.keys(), user_info.values()):print(k+v)
    else:print()
    print(tabulate.tabulate(result[1:], headers=result[0]))
    
def Main():
    option =parser.parse_args()[0]
    find =find_all(option)
    if not find:parser.print_help();return
    web_portal(option.regno, option.dob)

if __name__ == '__main__':
    help();Main()