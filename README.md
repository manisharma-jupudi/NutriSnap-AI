# 🥗 NutriSnap AI

**Your AI-powered nutrition assistant — snap it, track it, understand it.**

NutriSnap AI is an AI-powered nutrition assistant that helps users understand their meals through food images or text descriptions. Using Google's Gemini AI, the application identifies food items and provides estimated calories, protein, carbohydrates, and fat in a simple conversational interface.

## ✨ Features

- 📸 **Meal Photo Analysis:** Upload a food image to identify the meal and estimate its nutritional values.
- 💬 **Text-Based Nutrition:** Describe what you eat and receive a nutritional breakdown.
- 🔥 **Calorie Estimation:** Get approximate calorie information for meals.
- 🥗 **Macronutrient Tracking:** Estimate protein, carbohydrates, and fat.
- 👤 **Personalized Welcome:** Start with your name and WhatsApp number.
- 📲 **WhatsApp Integration:** Supports WhatsApp messaging through Twilio, subject to Twilio Sandbox, account, and template requirements.
- 🤖 **AI-Powered Responses:** Use Google's Gemini API to generate friendly, conversational nutrition estimates.

> **Disclaimer:** Nutrition values generated from meal descriptions and photos are estimates, not medical advice. Actual values depend on portion sizes, ingredients, and preparation methods.

## 🛠️ Technology Stack

- **Frontend and application:** Streamlit
- **AI model integration:** Google Gemini API using `google-genai`
- **WhatsApp messaging:** Twilio API
- **Image processing:** Pillow
- **Programming language:** Python

## 📁 Project Structure

```text
NutriSnap-AI/
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```

The actual `secrets.toml` file contains private credentials and must not be committed to GitHub.

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/manisharma-jupudi/NutriSnap-AI.git
cd NutriSnap-AI
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure API credentials

Create the secrets file:

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and enter your own credentials:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
GEMINI_MODEL = "your-configured-gemini-model"
TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
TWILIO_WHATSAPP_NUMBER = "your-twilio-whatsapp-sender"
```

Use the model name supported by your Gemini API account. Add other settings only if required by your application.

**Security:** Never commit real API keys, authentication tokens, or `.streamlit/secrets.toml` to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## 🔑 Required API Services

### Google Gemini API

NutriSnap AI uses Gemini to analyze meal descriptions and photos.

1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Obtain a Gemini API key.
3. Add it to `.streamlit/secrets.toml`.
4. Configure a model available to your account.

### Twilio WhatsApp

The application can integrate with Twilio for WhatsApp messaging. Configure the account SID, authentication token, and WhatsApp sender in your secrets file.

WhatsApp delivery depends on Twilio account permissions, Sandbox configuration, templates, and applicable WhatsApp messaging rules. Additional account setup or an upgrade may be required for some features.

## ☁️ Deployment

NutriSnap AI can be deployed using Streamlit Community Cloud.

1. Push the project to GitHub.
2. Visit [Streamlit Community Cloud](https://share.streamlit.io/).
3. Sign in using GitHub.
4. Create a new app and select this repository.
5. Set the branch to `main` and the main file to `app.py`.
6. Open the app settings and add your credentials under **Secrets**.
7. Deploy the application and test its features.

## 🚀 Future Improvements

- Daily calorie and macronutrient tracking
- Meal history and nutrition reports
- Personalized nutrition goals
- User profiles and progress dashboards
- Improved portion-size estimation
- Integration with additional health and fitness services

## 👨‍💻 Author

**Manisharma Jupudi**

GitHub: [@manisharma-jupudi](https://github.com/manisharma-jupudi)

## 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for the complete license text.
