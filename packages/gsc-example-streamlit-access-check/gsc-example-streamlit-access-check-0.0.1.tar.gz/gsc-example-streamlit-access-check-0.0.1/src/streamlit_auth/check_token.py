import threading, base64, json, jwt
import streamlit as st

def check_token_access(menuid, urlEncodedToken):
    # 서명 키
    sighKey = "VlwEyVBsYt9V7zq57TejMnVUyzblYcfPQye08f7MGVA9XkHa"

    # 서명 검증 및 클레임 추출
    try:
        claims = jwt.decode(urlEncodedToken, base64.b64decode(sighKey), algorithms=['HS256'])
    # print("claims =", claims)
        if "menuList" not in claims:
            raise Exception("menu 정보가 없는 토큰입니다.")
        #print("Subject =", claims["sub"])
        #print("menuList =", claims["menuList"])
    except jwt.ExpiredSignatureError:
        print("토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        print("유효하지 않은 토큰입니다.")
    except Exception as e:
        print(str(e))
        
    Subject = claims["sub"]
    
    # "menuList" 값을 JSON으로 파싱
    menu_list_json = json.loads(claims['menuList'])

    # 각 항목에서 "menuId" 값을 추출하여 리스트에 저장
    menu_ids = [item['menuId'] for item in menu_list_json]
    
    if menuid in menu_ids:
        return True
    else:
        st.write("Permission Denied")
        exit()
