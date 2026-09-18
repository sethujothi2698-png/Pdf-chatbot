        try:
            genai.configure(api_key=api_key)
            
            # Primary model set pandrom
            try:
                model = genai.GenerativeModel("gemini-3.6-flash")
            except Exception:
                model = genai.GenerativeModel("gemini-pro")

            full_prompt = f"Context from document:\n{pdf_text}\n\nQuestion: {prompt}\n\nPlease answer accurately using only the above context."

            with st.chat_message("assistant"):
                try:
                    response = model.generate_content(full_prompt, stream=True)
                    full_res = st.write_stream(chunk.text for chunk in response)
                except Exception:
                    # 503 error vandha backup model direct-a execute aagum
                    fallback_model = genai.GenerativeModel("gemini-pro")
                    response = fallback_model.generate_content(full_prompt)
                    st.markdown(response.text)
                    full_res = response.text
                    
                st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"Error: {e}")
