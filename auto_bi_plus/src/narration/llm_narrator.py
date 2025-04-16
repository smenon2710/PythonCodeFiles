# auto_bi_plus/src/narration/llm_narrator.py

from transformers import pipeline

# Using FLAN-T5 or similar open-source model
generator = pipeline("text2text-generation", model="google/flan-t5-base")

def generate_forecast_narrative(metric_name: str, forecast_df):
    latest = forecast_df.iloc[-1]
    yhat = latest['yhat']
    yhat_lower = latest['yhat_lower']
    yhat_upper = latest['yhat_upper']
    date = latest['ds'].strftime('%Y-%m-%d')

    prompt = (
        f"Generate a business insight based on this forecast:\n"
        f"Metric: {metric_name}\n"
        f"Forecast Date: {date}\n"
        f"Predicted Value: {yhat:.2f}\n"
        f"Range: [{yhat_lower:.2f}, {yhat_upper:.2f}]"
    )

    result = generator(prompt, max_length=100)[0]['generated_text']
    return result
