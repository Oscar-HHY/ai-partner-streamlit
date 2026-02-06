import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json
from streamlit import session_state
import uuid


st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

# 生成会话标识的函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def get_user_id():
    # 每个用户（每个浏览器会话）一个独立ID
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id


# 保存会话信息的函数
def save_session():
    if st.session_state.current_session:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        user_dir = get_user_sessions_dir()
        with open(os.path.join(user_dir, f"{st.session_state.current_session}.json"),
                  "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)



# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    user_dir = get_user_sessions_dir()

    file_list = os.listdir(user_dir)
    for filename in file_list:
        if filename.endswith(".json"):
            session_list.append(filename[:-5])

    session_list.sort(reverse=True)
    return session_list


# 加载指定会话信息
def load_session(session_name):
    try:
        user_dir = get_user_sessions_dir()
        path = os.path.join(user_dir, f"{session_name}.json")

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败！")


#删除会话信息
def delete_session(session_name):
    try:
        user_dir = get_user_sessions_dir()
        path = os.path.join(user_dir, f"{session_name}.json")

        if os.path.exists(path):
            os.remove(path)

        if session_name == st.session_state.current_session:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()

    except Exception:
        st.error("删除会话失败！")


# 获取用户会话目录
def get_user_sessions_dir():
    user_id = get_user_id()
    user_dir = os.path.join("sessions", user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir




# 标题
st.title("AI智能伴侣")

#logo
st.logo("references/logo.png")
if os.path.exists("references/logo.png"):
    st.logo("references/logo.png")

#系统提示词
system_prompt = """
        你叫 %s，现在是用户的真实伴侣，请完全代入伴侣角色。:
        规则:
            1.每次只回1条消息
            2.禁止任何场景或状态描述性文字
            3.匹配用户的语言
            4.回复简短，像微信聊天一样
            5.有需要的话可以用等emoji表情
            6.用符合伴侣性格的方式对话
            7.回复的内容，要充分体现伴侣的性格特征
        伴侣性格:
            -%s
        你必须严格遵守上述规则来回复用户。
        """

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []   # session_state就是缓存信息，让页面刷新后数据不丢失

#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = '小甜甜'

#性格
if "nature" not in st.session_state:
    st.session_state.nature = '活泼开朗的东北姑娘'

# 会话名字
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 获取用户ID
get_user_id()


#展示聊天信息
st.text(f"会话名称: {st.session_state.current_session}")
for message in st.session_state.messages: # {"role": "user", "content": "Hello"}
    st.chat_message(message['role']).write(message["content"])

    # if message["role"] == "user":
    #     st.chat_message('user').write(message["content"])
    # else:
    #     st.chat_message('assistant').write(message["content"])


#创建与DeepSeek API进行交互（DEEPSEEK_API_KEY 是环境变量的名字，其实就是DeepSeek的API Key）
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

#左侧的侧边栏 - with: streamlit中上下文管理器
with st.sidebar:
    # 会话信息
    st.subheader("AI 控制面板")

    # 新建会话
    if st.button("新建会话", use_container_width =  True, icon = '🐱'):
        # 1. 保存会话信息
        save_session()

        # 2. 创建新的会话
        if st.session_state.messages: # 如果有消息，是True，否则为False
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()  # 重新运行当前页面
    # 会话历史
    st.text("历史记录")
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        with col1:
            #加载会话信息
            # 三元运算符： 如果条件为真，则返回第一个表达式的值，否则返回第二个表达式的值 -----> 语法： 值1 if 条件 else 值2
            if st.button(session,use_container_width =  True, icon='📓', key = f'load_{session}', type = "primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            #删除会话信息
            if st.button("", use_container_width =  True, icon = "❌️", key = f'delete_{session}'):
                delete_session(session)
                st.rerun()

        # st.button("session", icon='📓')
        # st.button("", icon = "❌️")

    # 分割线
    st.divider()

    #伴侣信息
    st.subheader("伴侣信息")
    #昵称
    nick_name = st.text_input("昵称", placeholder='请输入昵称', value = st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    #性格输入框
    nature = st.text_area("性格",  placeholder='请输入性格', value = st.session_state.nature)
    if nature:
        st.session_state.nature = nature



#消息输入框
prompt = st.chat_input("请输入你的问题")
if prompt:  # 字符串会自动转换为布尔值，如果字符串不为空，则返回True，否则返回False
    st.write(f'用户：{prompt}')
    st.chat_message('user').write(prompt)
    print("-----------> 调用AI大模型，提示词：", prompt)
    #保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用AI大模型(此处是DeepSeek)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            # {"role": "user", "content":  prompt},
            #解决会话记忆问题，这样的话，每次调用API时，都会将用户输入的提示词和AI大模型返回的回复保存到会话中，下次调用API时，会带上这些信息，从而实现会话记忆
            *st.session_state.messages
        ],
        stream=True
    )

    # 打印AI大模型返回的回复(这是非流式输出的解析方式)
    # print('<---------- 回复内容: ', response.choices[0].message.content)
    # st.chat_message('assistant').write(response.choices[0].message.content)

    # 打印AI大模型返回的回复(这是流式输出的解析方式)
    response_message = st.empty() # 创建一个空组件，用于显示AI大模型返回的回复

    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message('assistant').write(full_response)

    #保存AI大模型返回的回复
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    #保存会话信息
    save_session()