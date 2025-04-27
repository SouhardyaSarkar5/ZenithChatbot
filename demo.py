import requests

def generate_content(text):
    headers = {
        'Content-Type': 'application/json',
    }

    params = {
        'key': 'YOUR_API_KEY',  # Replace with your actual API key
    }

    json_data = {
        'contents': [
            {
                'parts': [
                    {
                        'text': text,
                    },
                ],
            },
        ],
    }

    response = requests.post(
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent',
        params=params,
        headers=headers,
        json=json_data,
    )

    if response.status_code == 200:
        response_json = response.json()
        poem = response_json['candidates'][0]['content']['parts'][0]['text']
        return poem
    else:
        return f"Request failed with status code {response.status_code}. Response text: {response.text}"

if __name__ == "__main__":
    while True:
        prompt = input("Please enter a prompt (or type 'bye' to exit): ")
        if prompt.lower() in ['bye', 'exit']:
            print("Goodbye!")
            break
        content = generate_content(prompt)
        print(content)
