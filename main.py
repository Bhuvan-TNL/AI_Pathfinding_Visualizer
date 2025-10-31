import streamlit as st

st.set_page_config(page_title="AI Pathfinding Visualizer", page_icon="🧠")

st.title("🧠 AI Pathfinding Visualizer")
st.markdown("""
Welcome!  
This tool demonstrates how algorithms like **A\***, **Dijkstra**, and **BFS** find paths through mazes —  
with an AI assistant that explains which one performs best.
""")

if st.button("Test App"):
    st.success("✅ Streamlit is working fine and ready to build!")
