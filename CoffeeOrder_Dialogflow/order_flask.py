import flask
import os
import pandas as pd
from flask import send_from_directory, request
import random
app = flask.Flask(__name__)

output_list = []
bot_repeat = []


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/favicon.png')


@app.route('/')
@app.route('/home')
def home():
    return "Hello World"


@app.route('/webhook', methods=['POST'])
def webhook():
    path = './order_coffee.csv'
    path_empty = './order_coffee_empty.csv'
    print('output_list : ', output_list)
    req = request.get_json(force=True)
    print(req)
    bot = ""
    list_input = [[], [], []]
    user = req['queryResult']['queryText']
    bot_intent = req['queryResult']['intent']['displayName']  # intent 입력

    print('User :', user)
    print("bot_intent : ", bot_intent)
    short_check = user.split()
    if '아아' in short_check or '뜨아' in short_check or '따아' in short_check:
        utter = "아아는 아이스 아메리카노 뜨아는 뜨거운 아메리카노 따아는 따뜻한 아메리카노 아바라는 아이스 바닐라라떼로 전체 이름으로 말씀해주세요"
        return {'fulfillmentText': utter}

    if bot_intent == '002_start_order':
        bot = "메뉴를 보고 알맞은 메뉴명, 온도, 수량을 천천히 말씀해주세요."

        return {
            'fulfillmentText': bot
        }

    if bot_intent == '002-1_menu_introduce':  # 전체 메뉴 출력
        bot = """
        ======Coffee======

        - 라테아트

        - 카페라떼

        - 카푸치노

        - 카페모카

        - 바닐라라떼

        - 카라멜마끼아또

        - 초코라떼

        - 초코밀크

        - 캬라멜밀크

        - 아메리카노

=======Ade=======

        - 자몽 에이드

        - 레몬 에이드

        - 청포도 에이드

=================

네, 이제 메뉴를 보고 알맞은 메뉴명, 온도, 수량을 천천히 말씀해주세요. 

        """

        return {
            'fulfillmentText': bot
        }

    if bot_intent == '003_order_process':

        menu = req['queryResult']['parameters']['menu']
        number = req['queryResult']['parameters']['number']
        temperature = req['queryResult']['parameters']['temperature']

        print("menu 리스트", menu)
        print("number 리스트", number)
        print("temperature 리스트", temperature)

        list_input[0] += menu
        list_input[1] += number
        list_input[2] += temperature

        order_coffee = pd.read_csv(path, encoding='utf-8')  # 데이터를 저장할 csv 파일 호출
        print("호출된 orderqueen 데이터프레임\n", order_coffee)

        menu_dict = {'라떼아트': 5000, '카페라떼': 5000, '카푸치노': 5000, '카페모카': 5000, '바닐라라떼': 6000,
                      '카라멜마끼아또': 6000, '초코라떼': 5000, '초코밀크': 4500,
                      '캬라멜 밀크': 4500, '아메리카노': 4500, '자몽 에이드': 5000, '레몬 에이드': 5000, '청포도 에이드': 5000}

        for i in range(0, len(menu), 1):
            order_coffee.loc[i, 'menu'] = menu[i]  # menu 열에 menu 값 입력
        for i in range(0, len(number), 1):
            order_coffee.loc[i, 'number'] = number[i]  # number 열에 number 값 입력
        for i in range(0, len(temperature), 1):
            order_coffee.loc[i, 'temperature'] = temperature[i]  # temperature 열에 temperature 값 입력
        for i in range(0, len(menu), 1):
            order_coffee.loc[i, 'cost'] = menu_dict[menu[i]]

        print('데이터 프레임에 입력된 값을 넣는다.\n')
        print(order_coffee)

        order_coffee = order_coffee.fillna(0)  # 데이터 프레임에서 NaN값을 0으로 대처한다.

        print('데이터 프레임에서 NaN값을 0으로 대처한다.\n')
        print(order_coffee)

        order_coffee_output = []  # 빈 리스트 생성
        for i in range(len(menu)):
            line = []  # 안쪽 리스트로 사용할 빈 리스트 생성
            order_coffee_output.append(line)

        print("menu, number, temperature 순서로 담아 놓을 리스트 생성(order_coffee_output) : ", order_coffee_output)

        for i in range(0, len(menu), 1):
            order_coffee_output[i].append(order_coffee.loc[i, 'menu'])
            order_coffee_output[i].append(order_coffee.loc[i, 'number'])
            order_coffee_output[i].append(order_coffee.loc[i, 'temperature'])

        print("데이터 입력 후의 order_coffee_output 리스트 : ", order_coffee_output)

        count = 0

        for i in range(0, len(order_coffee_output), 1):
            if 0 in order_coffee_output[i]:  # order_coffee_output의 각 리스트[menu, number, temperature]에 0이 들어 있을 경우
                count = count + 1  # count에 1을 더한다.

        print("존재하는 0의 빈도:", count)

        order_coffee.to_csv(path, index=False,
                          encoding='utf-8-sig')  # 데이터 프레임을 다시 csv파일로 저장한다.

        utter = ""
        t_low = ['차갑게', '시원하게']
        t_high = ['뜨겁게', '따뜻하게']
        n_dict = {'1': '한', '2': '두', '3': '세', '4': '네', '5': '다섯', '6': '여섯', '7': '일곱', '8': '여덟', '9': '아홉',
                  '10': '열'}

        if count == 0:  # 모든 order_coffee_output의 각 리스트[menu, number, temperature]에 0이 없는 경우 telegram으로 출력을 진행한다.
            print("리스트에 0이 존재하지 않습니다.")
            bot = ""
            for i in range(len(list_input[0])):
                t = ''
                if list_input[2][i] == 'ice':
                    choose_temp = random.randrange(0, 2)
                    t = t_low[choose_temp]
                elif list_input[2][i] == 'hot':
                    choose_temp = random.randrange(0, 2)
                    t = t_high[choose_temp]
                bot += '{} {} {}잔'.format(list_input[0][i], t, n_dict[list_input[1][i]])

                if i != len(list_input[0]) - 1:
                    bot += '과\n'

            bot = bot + " 맞으신가요?"
            bot += '\n\n'
            print("bot :", bot)

            bot_repeat.clear()  # 이전에 담겨 있던 것 삭제
            bot_repeat.append(bot)  # 뭐라고했는지 못들어서 다시 말해달라고 할때 사용

            return {
                'fulfillmentText': bot
            }

    if bot_intent == "003_order_process - repeat":
        bot = bot_repeat

        return {
            'fulfillmentText': bot
        }

    if bot_intent == '004_menu_edit':
        menu = req['queryResult']['parameters']['menu']
        number = req['queryResult']['parameters']['number']
        temperature = req['queryResult']['parameters']['temperature']

        print("menu 리스트", menu)
        print("number 리스트", number)
        print("temperature 리스트", temperature)

        list_input[0] += menu
        list_input[1] += number
        list_input[2] += temperature

        order_coffee = pd.read_csv(path, encoding='utf-8')  # 데이터를 저장할 csv 파일 호출
        print("호출된 order_coffee 데이터프레임\n", order_coffee)

        menu_dict = {'라떼아트': 5000, '카페라떼': 5000, '카푸치노': 5000, '카페모카': 5000, '바닐라라떼': 6000,
                      '카라멜마끼아또': 6000, '초코라떼': 5000, '초코밀크': 4500,
                      '캬라멜 밀크': 4500, '아메리카노': 4500, '자몽 에이드': 5000, '레몬 에이드': 5000, '청포도 에이드': 5000}

        print("추가하기 전 이미 들어가 있는 메뉴의 수",len(order_coffee))
        print("추가하기 전 데이터프레임")
        print(order_coffee)


        print(len(order_coffee))



        for i in range(0, len(menu), 1):
            new_data = {'menu': menu[i], 'number': number[i], 'temperature': temperature[i], 'cost': menu_dict[menu[i]]}
            order_coffee = order_coffee.append(new_data, ignore_index=True)


        print('데이터 프레임에 입력된 값을 넣는다.\n')
        print(order_coffee)



        order_coffee = order_coffee.fillna(0)  # 데이터 프레임에서 NaN값을 0으로 대처한다.

        print('데이터 프레임에서 NaN값을 0으로 대처한다.\n')
        print(order_coffee)

        order_coffee_output = []  # 빈 리스트 생성
        for i in range(len(menu)):
            line = []  # 안쪽 리스트로 사용할 빈 리스트 생성
            order_coffee_output.append(line)

        print("menu, number, temperature 순서로 담아 놓을 리스트 생성(order_coffee_output) : ", order_coffee_output)

        for i in range(0, len(menu), 1):
            order_coffee_output[i].append(order_coffee.loc[i, 'menu'])
            order_coffee_output[i].append(order_coffee.loc[i, 'number'])
            order_coffee_output[i].append(order_coffee.loc[i, 'temperature'])

        print("데이터 입력 후의 order_coffee_output 리스트 : ", order_coffee_output)

        count = 0

        for i in range(0, len(order_coffee_output), 1):
            if 0 in order_coffee_output[i]:  # order_coffee_output의 각 리스트[menu, number, temperature]에 0이 들어 있을 경우
                count = count + 1  # count에 1을 더한다.

        print("존재하는 0의 빈도:", count)

        order_coffee.to_csv(path, index=False,
                          encoding='utf-8-sig')  # 데이터 프레임을 다시 csv파일로 저장한다.

        utter = ""
        t_low = ['차갑게', '시원하게']
        t_high = ['뜨겁게', '따뜻하게']
        n_dict = {1: '한', 2: '두', 3: '세', 4: '네', 5: '다섯', 6: '여섯', 7: '일곱', 8: '여덟', 9: '아홉',
                  10: '열'}

        order_coffee1 = pd.read_csv(path, encoding='utf-8')

        result = [[], [], []]
        for i in range(len(order_coffee1)):
            result[0].append(order_coffee1.loc[i, 'menu'])
            result[1].append(order_coffee1.loc[i, 'number'])
            result[2].append(order_coffee1.loc[i, 'temperature'])

        print(result)

        if count == 0:  # 모든 order_coffee_output의 각 리스트[menu, number, temperature]에 0이 없는 경우 telegram으로 출력을 진행한다.
            print("리스트에 0이 존재하지 않습니다.")
            bot = ""
            for i in range(len(result[0])):
                t = ''
                if result[2][i] == 'ice':
                    choose_temp = random.randrange(0, 2)
                    t = t_low[choose_temp]
                elif result[2][i] == 'hot':
                    choose_temp = random.randrange(0, 2)
                    t = t_high[choose_temp]
                bot += '{} {} {}잔'.format(result[0][i], t, n_dict[int(result[1][i])])

                if i != len(result[0]) - 1:
                    bot += '과\n'

            bot = bot + " 맞으신가요?"
            bot += '\n\n'
            print("bot :", bot)

            bot_repeat.clear()  # 이전에 담겨 있던 것 삭제
            bot_repeat.append(bot)  # 뭐라고했는지 못들어서 다시 말해달라고 할때 사용

            return {
                'fulfillmentText': bot
            }

    if bot_intent == '006_payment':
        order_coffee_menu = []
        order_coffee_num = []
        order_coffee = pd.read_csv(path, encoding='utf-8')  # 데이터를 저장할 csv 파일 호출
        for i in range(0, len(order_coffee), 1):
            order_coffee_menu.append(order_coffee.loc[i, 'menu'])
            order_coffee_num.append(order_coffee.loc[i, 'number'])


        menu_dict_ = {'라떼아트': 5000, '카페라떼': 5000, '카푸치노': 5000, '카페모카': 5000, '바닐라라떼': 6000,
                     '카라멜마끼아또': 6000, '초코라떼': 5000, '초코밀크': 4500,
                     '캬라멜 밀크': 4500, '아메리카노': 4500, '자몽 에이드': 5000, '레몬 에이드': 5000, '청포도 에이드': 5000}

        cost = 0
        for c, n in zip(order_coffee_menu, order_coffee_num):
            cost += menu_dict_[c] * n
        print(list_input, '__________________________')
        utter = "총 {}원 결제가 완료되었습니다.\n이용해주셔서 감사합니다.\n이상 오더퀸 커피였습니다.".format(cost)

        order_coffee1 = pd.read_csv(path_empty,
                                 encoding='utf-8')  # 데이터를 저장할 csv 파일 호출


        order_coffee1.to_csv(path, index=False, encoding='utf-8-sig')
        order_coffee2 = pd.read_csv(path, encoding='utf-8')  # 데이터를 저장할 csv 파일 호출

        print('다음 사용자를 위해 데이터가 모두 초기화되었습니다')
        print(order_coffee2)
        return {
            'fulfillmentText': utter
        }

    return {
        'fulfillmentText': bot
    }

if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()
