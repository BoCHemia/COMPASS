import streamlit as st
import sys

print('Python %s on %s' % (sys.version, sys.platform))

def main():

    st.set_page_config(page_title="Run COMPASS", page_icon="🧭", layout="wide")

    pg = st.navigation([
        st.Page("pages/0_compass.py", title="COMPASS app", icon="🧭"),
        st.Page("pages/1_userguide.py", title="User guide", icon="⚙️"),
        st.Page("pages/2_about.py", title="About", icon=":material/info:"),
    ])
    pg.run()



if __name__ == '__main__':
    main()
    print('app is running')
    #todo: clear the user folder after the app is closed? or after a certain time period? to prevent storage issues when hosting in EAWAG
    # todo: The u should know that if they install the app locally, the data will be stored on their computer in the /data/_USER folder, and they can delete it whenever they want