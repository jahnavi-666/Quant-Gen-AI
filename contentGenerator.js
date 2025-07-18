function generateContent() {
        const topic = document.getElementById('topicInput').value;

        fetch('/generate_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: topic })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('result').innerText = data.generated_text;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}