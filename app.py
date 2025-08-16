import streamlit as st
import asyncio
from main import main  # Import your async main function

st.title("YouTube Experiment Agent")

notion_id = st.text_input("Enter Notion Page ID", "")
period = st.selectbox("Select Analysis Period", ["24hr", "48hr", "7d"])

if st.button("Run Analysis"):
    if notion_id and period:
        with st.spinner("Running analysis..."):
            # Run the async main function and display results
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(main(notion_id, period))
                st.success("Analysis complete! Check your Notion page for results.")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                loop.close()
    else:
        st.warning("Please enter a Notion ID and select a period.")