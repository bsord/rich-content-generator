# Rich Content Generator

## Setup
1. Create ```./streamlit/secrets.toml```
2. Add `password = "password here"` to secrets.toml:


## Run
1. `pip install -r requirements.txt`
2. `streamlit run app.py`
3. open `localhost:8501` in a browser

## Usage
1. Fill out inputs and click `Generate Teasers`
2. Select one of the 3 teasers returned (or modify inputs and generate teasers again)
3. Click `Generate Outline`
4. If you like the outline, click `Generate Content`, if not, click `Generate Outline` again until you have an outline you like
5. Once content is generated you can review, if you like it, click `Create PDF`, if not, click `Generate Outline` again.
6. Now that PDF is created, you can view it in the preview window or click `Download PDF` to get a local copy
7. Upload to your favorite tool to modify/pretty up your PDF