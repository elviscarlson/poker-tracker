import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Databashantering
def init_db():
    conn = sqlite3.connect('poker_tracker.db')
    c = conn.cursor()
    
    # Användartabell med admin-flagga
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  is_admin INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Sessionstabell
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  date DATE NOT NULL,
                  duration_hours REAL NOT NULL,
                  profit_loss REAL NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = sqlite3.connect('poker_tracker.db')
    c = conn.cursor()
    
    # Kolla om det är första användaren (blir då admin)
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    is_admin = 1 if user_count == 0 else 0
    
    try:
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                  (username, hash_password(password), is_admin))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def verify_user(username, password):
    conn = sqlite3.connect('poker_tracker.db')
    c = conn.cursor()
    c.execute("SELECT id, is_admin FROM users WHERE username = ? AND password = ?",
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result if result else None

def add_session(user_id, date, duration, profit_loss):
    conn = sqlite3.connect('poker_tracker.db')
    c = conn.cursor()
    c.execute("INSERT INTO sessions (user_id, date, duration_hours, profit_loss) VALUES (?, ?, ?, ?)",
              (user_id, date, duration, profit_loss))
    conn.commit()
    conn.close()

def get_sessions(user_id):
    conn = sqlite3.connect('poker_tracker.db')
    df = pd.read_sql_query(
        "SELECT * FROM sessions WHERE user_id = ? ORDER BY date DESC",
        conn, params=(user_id,))
    conn.close()
    return df

def delete_session(session_id):
    conn = sqlite3.connect('poker_tracker.db')
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('poker_tracker.db')
    df = pd.read_sql_query("SELECT id, username, created_at, is_admin FROM users ORDER BY created_at", conn)
    conn.close()
    return df

def get_user_stats(user_id):
    conn = sqlite3.connect('poker_tracker.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = c.fetchone()[0]
    conn.close()
    
    sessions_df = get_sessions(user_id)
    
    if len(sessions_df) == 0:
        return {
            'username': username,
            'total_sessions': 0,
            'total_profit': 0,
            'total_hours': 0,
            'avg_profit_per_session': 0,
            'avg_profit_per_hour': 0,
            'win_rate': 0
        }
    
    total_profit = sessions_df['profit_loss'].sum()
    total_sessions = len(sessions_df)
    total_hours = sessions_df['duration_hours'].sum()
    winning_sessions = len(sessions_df[sessions_df['profit_loss'] > 0])
    
    return {
        'username': username,
        'total_sessions': total_sessions,
        'total_profit': total_profit,
        'total_hours': total_hours,
        'avg_profit_per_session': total_profit / total_sessions if total_sessions > 0 else 0,
        'avg_profit_per_hour': total_profit / total_hours if total_hours > 0 else 0,
        'win_rate': (winning_sessions / total_sessions * 100) if total_sessions > 0 else 0
    }

# Initialisera databas
init_db()

# Session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Huvudapp
st.set_page_config(page_title="Poker Statistik Tracker", page_icon="🃏", layout="wide")

# Inloggning/Registrering
if st.session_state.user_id is None:
    st.title("🃏 Poker Statistik Tracker")
    
    tab1, tab2 = st.tabs(["Logga in", "Skapa konto"])
    
    with tab1:
        st.subheader("Logga in")
        login_username = st.text_input("Användarnamn", key="login_user")
        login_password = st.text_input("Lösenord", type="password", key="login_pass")
        
        if st.button("Logga in"):
            result = verify_user(login_username, login_password)
            if result:
                st.session_state.user_id = result[0]
                st.session_state.username = login_username
                st.session_state.is_admin = bool(result[1])
                st.rerun()
            else:
                st.error("Felaktigt användarnamn eller lösenord")
    
    with tab2:
        st.subheader("Skapa nytt konto")
        new_username = st.text_input("Välj användarnamn", key="new_user")
        new_password = st.text_input("Välj lösenord", type="password", key="new_pass")
        new_password_confirm = st.text_input("Bekräfta lösenord", type="password", key="new_pass_confirm")
        
        if st.button("Skapa konto"):
            if new_password != new_password_confirm:
                st.error("Lösenorden matchar inte")
            elif len(new_username) < 3:
                st.error("Användarnamnet måste vara minst 3 tecken")
            elif len(new_password) < 4:
                st.error("Lösenordet måste vara minst 4 tecken")
            else:
                if create_user(new_username, new_password):
                    st.success("Konto skapat! Du kan nu logga in.")
                else:
                    st.error("Användarnamnet är redan taget")

else:
    # Inloggad vy
    header_col1, header_col2 = st.columns([6, 1])
    with header_col1:
        title = f"🃏 Poker Statistik - {st.session_state.username}"
        if st.session_state.is_admin:
            title += " 👑"
        st.title(title)
    with header_col2:
        if st.button("Logga ut"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()
    
    # Hämta sessioner
    sessions_df = get_sessions(st.session_state.user_id)
    
    # Tabs - lägg till Admin-panel om användaren är admin
    if st.session_state.is_admin:
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Lägg till session", "📋 Alla sessioner", "👑 Admin Panel"])
    else:
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Lägg till session", "📋 Alla sessioner"])
    
    with tab1:
        if len(sessions_df) == 0:
            st.info("Du har inga pokersessioner än. Lägg till din första session i nästa flik!")
        else:
            # Beräkna statistik
            total_profit = sessions_df['profit_loss'].sum()
            total_sessions = len(sessions_df)
            total_hours = sessions_df['duration_hours'].sum()
            avg_profit_per_session = sessions_df['profit_loss'].mean()
            avg_profit_per_hour = total_profit / total_hours if total_hours > 0 else 0
            winning_sessions = len(sessions_df[sessions_df['profit_loss'] > 0])
            losing_sessions = len(sessions_df[sessions_df['profit_loss'] < 0])
            breakeven_sessions = len(sessions_df[sessions_df['profit_loss'] == 0])
            win_rate = (winning_sessions / total_sessions * 100) if total_sessions > 0 else 0
            best_session = sessions_df['profit_loss'].max()
            worst_session = sessions_df['profit_loss'].min()
            
            # KPI:er
            st.subheader("📈 Sammanfattning")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Vinst/Förlust", f"{total_profit:,.0f} kr", 
                         delta=f"{avg_profit_per_session:,.0f} kr/session")
            with col2:
                st.metric("Antal Sessioner", total_sessions,
                         delta=f"{win_rate:.1f}% vinst")
            with col3:
                st.metric("Total Speltid", f"{total_hours:.1f} h",
                         delta=f"{avg_profit_per_hour:,.0f} kr/h")
            with col4:
                st.metric("Bästa Session", f"{best_session:,.0f} kr",
                         delta=f"Sämsta: {worst_session:,.0f} kr", delta_color="off")
            
            st.divider()
            
            # Grafer
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Kumulativ Vinst/Förlust")
                sessions_df['date'] = pd.to_datetime(sessions_df['date'])
                sessions_df = sessions_df.sort_values('date')
                sessions_df['cumulative'] = sessions_df['profit_loss'].cumsum()
                
                fig = px.line(sessions_df, x='date', y='cumulative',
                            labels={'cumulative': 'Kumulativ vinst (kr)', 'date': 'Datum'},
                            markers=True)
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🎯 Sessionsresultat")
                result_data = pd.DataFrame({
                    'Resultat': ['Vinstsessioner', 'Förlustssessioner', 'Breakeven'],
                    'Antal': [winning_sessions, losing_sessions, breakeven_sessions]
                })
                fig = px.pie(result_data, values='Antal', names='Resultat',
                           color='Resultat',
                           color_discrete_map={'Vinstsessioner': '#2ecc71', 
                                              'Förlustssessioner': '#e74c3c',
                                              'Breakeven': '#95a5a6'})
                st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Vinst per session")
                fig = px.bar(sessions_df.head(20), x='date', y='profit_loss',
                           labels={'profit_loss': 'Vinst/Förlust (kr)', 'date': 'Datum'},
                           color='profit_loss',
                           color_continuous_scale=['red', 'yellow', 'green'],
                           color_continuous_midpoint=0)
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("⏱️ Vinst per timme")
                sessions_df['hourly_rate'] = sessions_df['profit_loss'] / sessions_df['duration_hours']
                fig = px.bar(sessions_df.head(20), x='date', y='hourly_rate',
                           labels={'hourly_rate': 'kr/timme', 'date': 'Datum'},
                           color='hourly_rate',
                           color_continuous_scale=['red', 'yellow', 'green'],
                           color_continuous_midpoint=0)
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                st.plotly_chart(fig, use_container_width=True)
            
            # Detaljerad statistik
            st.divider()
            st.subheader("📉 Detaljerad Statistik")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Session Statistik**")
                st.write(f"- Längsta session: {sessions_df['duration_hours'].max():.1f} h")
                st.write(f"- Kortaste session: {sessions_df['duration_hours'].min():.1f} h")
                st.write(f"- Genomsnittlig session: {sessions_df['duration_hours'].mean():.1f} h")
                
            with col2:
                st.write("**Vinst/Förlust**")
                st.write(f"- Median vinst: {sessions_df['profit_loss'].median():,.0f} kr")
                st.write(f"- Standardavvikelse: {sessions_df['profit_loss'].std():,.0f} kr")
                total_wins = sessions_df[sessions_df['profit_loss'] > 0]['profit_loss'].sum()
                total_losses = abs(sessions_df[sessions_df['profit_loss'] < 0]['profit_loss'].sum())
                st.write(f"- Totala vinster: {total_wins:,.0f} kr")
                st.write(f"- Totala förluster: {total_losses:,.0f} kr")
                
            with col3:
                st.write("**Trender**")
                last_5 = sessions_df.head(5)['profit_loss'].sum()
                last_10 = sessions_df.head(10)['profit_loss'].sum()
                st.write(f"- Senaste 5 sessionerna: {last_5:,.0f} kr")
                st.write(f"- Senaste 10 sessionerna: {last_10:,.0f} kr")
                if len(sessions_df) >= 2:
                    trend = "Uppåtgående" if sessions_df.head(5)['profit_loss'].sum() > sessions_df.tail(5)['profit_loss'].sum() else "Nedåtgående"
                    st.write(f"- Trend: {trend}")
    
    with tab2:
        st.subheader("Lägg till ny pokersession")
        
        col1, col2 = st.columns(2)
        
        with col1:
            session_date = st.date_input("Datum", value=datetime.now())
            duration = st.number_input("Speltid (timmar)", min_value=0.1, max_value=24.0, 
                                      value=2.0, step=0.5)
        
        with col2:
            profit_loss = st.number_input("Vinst/Förlust (kr)", 
                                         value=0.0, step=100.0,
                                         help="Positivt tal för vinst, negativt för förlust")
            st.write("")  # Spacing
            st.write("")
            
        if st.button("💾 Spara session", type="primary"):
            add_session(st.session_state.user_id, session_date, duration, profit_loss)
            st.success("Session sparad!")
            st.rerun()
    
    with tab3:
        st.subheader("Alla dina sessioner")
        
        if len(sessions_df) == 0:
            st.info("Inga sessioner att visa")
        else:
            # Formatera dataframe för visning
            display_df = sessions_df.copy()
            display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
            display_df['profit_loss'] = display_df['profit_loss'].apply(lambda x: f"{x:,.0f} kr")
            display_df['duration_hours'] = display_df['duration_hours'].apply(lambda x: f"{x:.1f} h")
            
            # Visa tabell
            st.dataframe(
                display_df[['date', 'duration_hours', 'profit_loss']].rename(columns={
                    'date': 'Datum',
                    'duration_hours': 'Speltid',
                    'profit_loss': 'Vinst/Förlust'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Radera session
            st.divider()
            st.subheader("🗑️ Ta bort session")
            session_to_delete = st.selectbox(
                "Välj session att ta bort",
                options=sessions_df['id'].tolist(),
                format_func=lambda x: f"{sessions_df[sessions_df['id']==x]['date'].values[0]} - {sessions_df[sessions_df['id']==x]['profit_loss'].values[0]:,.0f} kr"
            )
            
            if st.button("Ta bort vald session", type="secondary"):
                delete_session(session_to_delete)
                st.success("Session borttagen!")
                st.rerun()
    
    # Admin Panel
    if st.session_state.is_admin:
        with tab4:
            st.subheader("👑 Admin Panel")
            st.write("Här kan du se alla användare och deras statistik.")
            
            # Hämta alla användare
            users_df = get_all_users()
            
            st.divider()
            st.subheader("📊 Översikt alla användare")
            
            # Visa sammanfattande statistik
            all_stats = []
            for _, user in users_df.iterrows():
                stats = get_user_stats(user['id'])
                all_stats.append(stats)
            
            stats_df = pd.DataFrame(all_stats)
            
            if len(stats_df) > 0:
                # Sammanfattande kort
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Totalt antal användare", len(users_df))
                with col2:
                    active_users = len(stats_df[stats_df['total_sessions'] > 0])
                    st.metric("Aktiva användare", active_users)
                with col3:
                    total_sessions_all = stats_df['total_sessions'].sum()
                    st.metric("Totalt antal sessioner", int(total_sessions_all))
                with col4:
                    total_profit_all = stats_df['total_profit'].sum()
                    st.metric("Total vinst/förlust (alla)", f"{total_profit_all:,.0f} kr")
                
                st.divider()
                
                # Detaljerad tabell
                st.subheader("Användare i detalj")
                display_stats = stats_df.copy()
                display_stats['total_profit'] = display_stats['total_profit'].apply(lambda x: f"{x:,.0f} kr")
                display_stats['avg_profit_per_session'] = display_stats['avg_profit_per_session'].apply(lambda x: f"{x:,.0f} kr")
                display_stats['avg_profit_per_hour'] = display_stats['avg_profit_per_hour'].apply(lambda x: f"{x:,.0f} kr/h")
                display_stats['total_hours'] = display_stats['total_hours'].apply(lambda x: f"{x:.1f} h")
                display_stats['win_rate'] = display_stats['win_rate'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(
                    display_stats[['username', 'total_sessions', 'total_hours', 'total_profit', 
                                  'avg_profit_per_session', 'avg_profit_per_hour', 'win_rate']].rename(columns={
                        'username': 'Användarnamn',
                        'total_sessions': 'Sessioner',
                        'total_hours': 'Timmar',
                        'total_profit': 'Total vinst/förlust',
                        'avg_profit_per_session': 'Snitt/session',
                        'avg_profit_per_hour': 'Snitt/timme',
                        'win_rate': 'Vinst%'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.divider()
                
                # Välj användare för detaljerad vy
                st.subheader("🔍 Se detaljer för specifik användare")
                selected_user = st.selectbox(
                    "Välj användare",
                    options=users_df['id'].tolist(),
                    format_func=lambda x: users_df[users_df['id']==x]['username'].values[0]
                )
                
                if selected_user:
                    user_sessions = get_sessions(selected_user)
                    selected_username = users_df[users_df['id']==selected_user]['username'].values[0]
                    
                    st.write(f"### Sessioner för {selected_username}")
                    
                    if len(user_sessions) == 0:
                        st.info(f"{selected_username} har inga sessioner än.")
                    else:
                        # Visa användarens statistik
                        user_stats = get_user_stats(selected_user)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total vinst/förlust", f"{user_stats['total_profit']:,.0f} kr")
                        with col2:
                            st.metric("Antal sessioner", user_stats['total_sessions'])
                        with col3:
                            st.metric("Vinst per timme", f"{user_stats['avg_profit_per_hour']:,.0f} kr/h")
                        
                        # Visa graf
                        user_sessions['date'] = pd.to_datetime(user_sessions['date'])
                        user_sessions = user_sessions.sort_values('date')
                        user_sessions['cumulative'] = user_sessions['profit_loss'].cumsum()
                        
                        fig = px.line(user_sessions, x='date', y='cumulative',
                                    labels={'cumulative': 'Kumulativ vinst (kr)', 'date': 'Datum'},
                                    markers=True,
                                    title=f"Kumulativ vinst/förlust för {selected_username}")
                        fig.add_hline(y=0, line_dash="dash", line_color="gray")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Visa sessioner
                        display_user_sessions = user_sessions.copy()
                        display_user_sessions['date'] = display_user_sessions['date'].dt.strftime('%Y-%m-%d')
                        display_user_sessions['profit_loss'] = display_user_sessions['profit_loss'].apply(lambda x: f"{x:,.0f} kr")
                        display_user_sessions['duration_hours'] = display_user_sessions['duration_hours'].apply(lambda x: f"{x:.1f} h")
                        
                        st.dataframe(
                            display_user_sessions[['date', 'duration_hours', 'profit_loss']].rename(columns={
                                'date': 'Datum',
                                'duration_hours': 'Speltid',
                                'profit_loss': 'Vinst/Förlust'
                            }),
                            use_container_width=True,
                            hide_index=True
                        )