# YouTube Content Analysis Agent

An AI-powered agent for analyzing YouTube video performance, comparing metrics against historical baselines, and generating actionable reports. The agent integrates with Notion for experiment tracking and uses OpenAI for intelligent evaluation and reporting. The Streamlit interface makes it easy to run analyses and view results.

## 🎯 Use Cases

This agent is designed for YouTube creators, analysts, and experimenters who want to:

- **Analyze video performance** using YouTube Analytics
- **Compare new videos to historical baselines** for key metrics
- **Track experiments and hypotheses** in Notion
- **Generate AI-powered reports** and recommendations
- **Automate data collection** for previous videos

Perfect for:
- Content creators running A/B tests or creative experiments
- Teams tracking video performance and hypotheses in Notion
- Anyone seeking actionable insights from YouTube analytics

## 🚀 Features

- **YouTube Analytics Integration**: Fetches detailed video stats via the YouTube API
- **Baseline Comparison**: Compares new video metrics to historical averages
- **Notion Sync**: Reads and updates experiment pages in Notion
- **AI Evaluation**: Uses OpenAI agents for performance analysis and report generation
- **Streamlit Web Interface**: Simple UI for running analyses and viewing results
- **Database Storage**: Stores video stats in a local SQLite database
- **Batch Upload**: Easily populate the database with stats from previous videos

## 🔧 How It Works

The agent follows this workflow:

1. **Experiment Setup**: Track your video experiment in Notion
2. **Run Analysis**: Use the Streamlit app to analyze a video and update Notion
3. **Fetch Video Stats**: [`src.yt.get_all_video_stats`](src/yt.py) retrieves YouTube metrics
4. **Store Results**: [`src.db.store_video_stats`](src/db.py) saves stats in `video_stats.db`
5. **Baseline Calculation**: [`src.db.get_video_baseline`](src/db.py) computes historical averages
6. **AI Evaluation**: [`src.openai.run_evaluation_agent`](src/openai.py) compares results and generates insights
7. **Report Generation**: [`src.openai.run_report_agent`](src/openai.py) creates a human-readable summary
8. **Notion Update**: [`src.notion.notion_send_report`](src/notion.py) and [`src.notion.notion_update_hypothesis_result`](src/notion.py) update your Notion page

### APIs Used

- **YouTube Data API**: For video analytics
- **OpenAI GPT-4o**: For evaluation and reporting
- **Notion API**: For experiment tracking and updates

## 📋 Prerequisites

- Python 3.8+
- YouTube Data API credentials
- OpenAI API key
- Notion API key and access to your experiment database

## ⚙️ Environment Setup

Create a `.env` file in the project root:

```env
GOOGLE_CLOUD_API_KEY=your-youtube-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REFRESH_TOKEN=your-google-refresh-token

OPENAI_API_KEY=your-openai-api-key

NOTION_API_KEY=your-notion-api-key
```

### Getting API Keys

- **YouTube API**: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- **OpenAI API**: [OpenAI API Keys](https://platform.openai.com/api-keys)
- **Notion API**: [Notion Integration](https://www.notion.so/my-integrations)

## 🔧 Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd content-analysis-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the Streamlit application:
```bash
streamlit run app.py
```

5. Open your browser to `http://localhost:8501`

### Project Structure

```
content-analysis-agent/
├── app.py                 # Streamlit web interface
├── main.py                # Async analysis workflow
├── pull.py                # CLI for batch stats refresh
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .env.example           # Environment template
├── video_stats.db         # SQLite database for video stats
├── src/
│   ├── comparison.py      # Baseline comparison logic
│   ├── db.py              # Database functions
│   ├── notion.py          # Notion API integration
│   ├── openai.py          # OpenAI agent logic
│   └── yt.py              # YouTube API integration
```

## 🎬 Usage

### Web Interface

1. **Start the application**:
```bash
streamlit run app.py
```

2. **Enter Notion Page ID** and select analysis period (`24hr`, `48hr`, `7d`)
3. **Click "Run Analysis"** to fetch stats, compare to baseline, and update Notion

### Batch Upload Previous Videos

To populate the database with stats for your previous videos, use the CLI:

```bash
python pull.py --video-id <YOUR_VIDEO_ID>
```

- This will fetch stats for the specified video and store them in `video_stats.db`
- Repeat for each video you want to add as baseline data

### Processing Steps

- **Fetch Video Metadata**: [`src.yt.get_video_metadata`](src/yt.py)
- **Fetch Video Stats**: [`src.yt.get_all_video_stats`](src/yt.py)
- **Store in DB**: [`src.db.store_video_stats`](src/db.py)
- **Compare to Baseline**: [`src.comparison.compare_to_baseline`](src/comparison.py)
- **AI Evaluation**: [`src.openai.run_evaluation_agent`](src/openai.py)
- **Report Generation**: [`src.openai.run_report_agent`](src/openai.py)
- **Notion Update**: [`src.notion.notion_send_report`](src/notion.py)

## 🛠️ Configuration

- Edit `.env` for API credentials
- Adjust analysis periods as needed (`24hr`, `48hr`, `7d`)
- Use [`pull.py`](pull.py) for batch database population

## 🐛 Troubleshooting

- **API Errors**: Check credentials in `.env`
- **Database Issues**: Ensure `video_stats.db` is writable
- **Notion Sync**: Verify Notion API key and page permissions
- **YouTube API Quotas**: Monitor usage in Google Cloud Console

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various video IDs and Notion pages
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check console output for error messages
- Verify API keys and permissions
- Review `.env` configuration

## 👨‍💻 Credits

Created by **Tom Shaw** - [https://github.com/IAmTomShaw](https://github.com/IAmTomShaw)

This project demonstrates the power of combining YouTube analytics, Notion tracking, and OpenAI agents for creative