# CTagger Web app
Web form for CTagger and also include a automated tag suggestion experimental feature using calls to OpenAI.

### Installation
- Clone the repo
- Create `.env` file and specify a single line
`OPENAI_API_KEY=xxxxxx`
- Run `docker build -t ctagger .` in the top-level directory
- Run `docker run -p 8080:5000 ctagger`
- The app can be accessed with `https://localhost:8080`
**Warning: if it works this might incur a large charge to the OpenAI account**

Author: Dung "Young" Truong - May 2025