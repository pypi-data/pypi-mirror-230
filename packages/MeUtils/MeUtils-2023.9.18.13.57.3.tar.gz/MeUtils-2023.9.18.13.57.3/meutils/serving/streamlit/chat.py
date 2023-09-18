#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chat
# @Time         : 2023/8/23 12:01
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
import streamlit as st


def do_chat(
        user_role='user',

        assistant_role='assistant',
        assistant_avator="nesc.jpeg",

        reply_func=lambda input: f'{input}的答案',
        max_turns=3,
):
    def chat_message(role):
        if role == 'user':
            return st.chat_message(user_role)
        else:
            return st.chat_message(assistant_role, avatar=assistant_avator)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    else:
        st.session_state.messages = st.session_state.messages[-2 * (max_turns - 1):]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with chat_message(message.role):
            st.markdown(message.content, unsafe_allow_html=True)

    prompt = st.chat_input("    🔥请提问？")
    if prompt:
        print('\n')
        print(prompt)

        # Display user message in chat message container
        with chat_message(user_role):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append(ChatMessage(role=user_role, content=prompt))

        with chat_message(assistant_role):
            message_placeholder = st.empty()

            response = ''
            gen = reply_func(prompt) or '根据已知信息无法召回相关内容。'
            for token in gen:
                # Display robot response in chat message container
                response += token
                message_placeholder.markdown(response + "▌")
            message_placeholder.markdown(response, unsafe_allow_html=True)

        # Add robot response to chat history
        st.session_state.messages.append(ChatMessage(role=assistant_role, content=response))


class ChatMessage(BaseModel):
    role: str
    content: str
