import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Fitness Progress Tracker",
    page_icon="💪",
    layout="wide"
)

# --- CONSTANTS & INITIALIZATION ---
CSV_FILE = 'workouts.csv'
DATE_FORMAT = '%Y-%m-%d'

def initialize_csv():
    """
    Creates the CSV file with headers if it doesn't exist.
    Also adds some sample data for a better first-time experience.
    """
    if not os.path.exists(CSV_FILE):
        # Create a new DataFrame with sample data
        sample_data = {
            'date': ['2025-07-01', '2025-07-03', '2025-07-07', '2025-07-10', '2025-07-02', '2025-07-05', '2025-07-09'],
            'activity': ['Running', 'Running', 'Running', 'Running', 'Push-ups', 'Push-ups', 'Push-ups'],
            'value': [2.5, 2.8, 3.2, 4.5, 30, 35, 38],
            'metric': ['km', 'km', 'km', 'km', 'reps', 'reps', 'reps']
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(CSV_FILE, index=False)
        st.toast(f"Created data file with sample data: {CSV_FILE}")

def load_data():
    """
    Loads workout data from the CSV file.
    Returns an empty DataFrame if the file doesn't exist or is empty.
    """
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return pd.DataFrame(columns=['date', 'activity', 'value', 'metric'])
    
    try:
        df = pd.read_csv(CSV_FILE)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=['date', 'activity', 'value', 'metric'])

# --- APP LAYOUT ---

# Initialize the data file on first run
initialize_csv()

# Load the data
df = load_data()

st.title("💪 Fitness Progress Tracker")
st.markdown("Log your workouts, visualize your gains, and crush your goals.")

# --- SIDEBAR FOR DATA ENTRY ---
with st.sidebar:
    st.header("Log New Workout")
    
    with st.form("workout_form", clear_on_submit=True):
        date = st.date_input("Date", value="today")
        activity = st.text_input("Activity", placeholder="e.g., Running, Push-ups").strip().title()
        value = st.number_input("Value", min_value=0.0, format="%.2f", step=0.1)
        metric = st.text_input("Metric", placeholder="e.g., km, reps, kg").strip()
        
        submitted = st.form_submit_button("Log Workout")
        
        if submitted:
            if not activity or not metric:
                st.warning("Activity and Metric fields cannot be empty.")
            else:
                new_workout = pd.DataFrame([{
                    'date': date.strftime(DATE_FORMAT),
                    'activity': activity,
                    'value': value,
                    'metric': metric
                }])
                
                # Append to the CSV file
                new_workout.to_csv(CSV_FILE, mode='a', header=not os.path.exists(CSV_FILE), index=False)
                st.success("Workout logged successfully!")
                # We don't need to manually reload data, Streamlit's execution flow handles it.

# --- MAIN PAGE TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Progress Dashboard", "📈 View Full Log", "ℹ️ About"])

with tab1:
    st.header("Progress Dashboard")
    
    if df.empty:
        st.info("No workouts logged yet. Add a workout in the sidebar to get started!")
    else:
        # --- ACTIVITY SELECTION ---
        activities = df['activity'].unique()
        selected_activity = st.selectbox("Select an activity to visualize:", activities)
        
        # Filter data for the selected activity
        activity_df = df[df['activity'] == selected_activity].sort_values(by='date')
        
        if activity_df.empty:
            st.warning(f"No data found for '{selected_activity}'.")
        else:
            metric = activity_df['metric'].iloc[0]

            col1, col2 = st.columns([3, 1])

            with col1:
                # --- PROGRESS CHART ---
                st.subheader(f"Progress for {selected_activity}")
                fig = px.line(
                    activity_df, 
                    x='date', 
                    y='value', 
                    markers=True,
                    title=f"{selected_activity} Performance Over Time",
                    labels={'date': 'Date', 'value': f'Value ({metric})'}
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title=f"{metric.title()}",
                    title_x=0.5,
                    template="plotly_white"
                )
                fig.update_traces(line=dict(color='indigo', width=2), marker=dict(size=8))
                
                # --- GOAL LINE ---
                goal = st.number_input(f"Set a goal for {metric}:", min_value=0.0, value=0.0, step=1.0, key=f"goal_{selected_activity}")
                if goal > 0:
                    fig.add_hline(y=goal, line_dash="dash", line_color="green", annotation_text=f"Goal: {goal}", annotation_position="bottom right")

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # --- PERFORMANCE SUMMARY ---
                st.subheader("Summary")
                
                # Peak Performance
                peak_perf = activity_df['value'].max()
                peak_date = activity_df.loc[activity_df['value'].idxmax()]['date'].strftime(DATE_FORMAT)
                st.metric(label="Peak Performance", value=f"{peak_perf:.2f} {metric}", delta=f"on {peak_date}")
                
                # Most Recent Workout
                latest_perf = activity_df['value'].iloc[-1]
                latest_date = activity_df['date'].iloc[-1].strftime(DATE_FORMAT)
                st.metric(label="Most Recent", value=f"{latest_perf:.2f} {metric}", delta=f"on {latest_date}")

                # Calculate progress from first to last workout
                if len(activity_df) > 1:
                    first_val = activity_df['value'].iloc[0]
                    latest_val = activity_df['value'].iloc[-1]
                    total_progress = latest_val - first_val
                    st.metric(label="Total Progress", value=f"{total_progress:+.2f} {metric}", delta="Since first workout")
                else:
                    st.metric(label="Total Progress", value="N/A", delta="Need more data")
                    
with tab2:
    st.header("Full Workout Log")
    if df.empty:
        st.info("No workouts logged yet.")
    else:
        # Display the dataframe, sorted by most recent first
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True, hide_index=True)

with tab3:
    st.header("About This App")
    st.write("""
    This application helps you track and visualize your fitness progress over time.
    
    **How to use:**
    1.  **Log a Workout:** Use the form in the sidebar to add your daily workout details.
    2.  **View Dashboard:** In the 'Progress Dashboard' tab, select an activity to see your progress chart and performance summary. You can also set a goal to visualize it on the chart.
    3.  **Check Full Log:** The 'View Full Log' tab shows a complete history of all your logged workouts.
    
    All your data is stored locally in a `workouts.csv` file in the same directory as the app.
    """)

