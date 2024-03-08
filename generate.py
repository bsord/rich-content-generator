import openai

def get_cover_previews(content_type: str, topic: str):
    # Define TypeScript interfaces
    typescript_schema = """
    interface Cover {
      title: string;
      subtext: string;
      author: string;
      photo: string; //fake unsplash url
    }

    interface 3CoversResult {
      covers: Cover[];
      timestamp: number;
    }
    """

    prompt = f"""
    Given the following TypeScript interfaces:

    {typescript_schema}

    Give me 3 example covers for digital content of type {content_type} about {topic} returned as a json representation of a 3CoversResult
    """
    
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format= { "type": "json_object" },
            messages=[
                {
                    "role": "system",
                    "content": "You are an API that generates an array of 3 covers of digital content."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
                
            ],
        )
        print("generated")
    except Exception as e:
        return {"error": str(e)}

    # Formatting the response to only include the generated text
    response_json = completion.choices[0].message.content
    
    # Returning the response in a JSON object format
    return response_json


def get_outline_previews(title: str, subtext: str):

    # Define TypeScript interfaces
    typescript_schema = """

    interface Point {
        text: string;
    }

    interface Contents {
        title: string;
        points: Point[];
    }

    interface Outline {
      overview: string; // paragraph with atleast 4 sentences
      tableOfContents: Contents[]; // atleast 7 items in the table of contents
    }

    interface OutlineResult {
      outline: Outline;
      timestamp: number;
    }
    """

    prompt = f"""
    Given the following TypeScript interfaces:

    {typescript_schema}

    Give me a full outline for a piece of digital content with a title of {title} and a subtext of {subtext} returned as a json representation of a OutlineResult
    """
    
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format= { "type": "json_object" },
            messages=[
                {
                    "role": "system",
                    "content": "You are an API that generates overviews and outlines for digital content."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
                
            ],
        )
        print("generated")
    except Exception as e:
        return {"error": str(e)}

    # Formatting the response to only include the generated text
    response_json = completion.choices[0].message.content

    # Returning the response in a JSON object format
    return response_json

def hydrate_content_section(tableOfContents: str, overview: str, title: str, point: str):

    # Define TypeScript interfaces
    typescript_schema = """
    interface ParagraphContent {
      content: string; 
    }

    interface BodyResult {
      paragraphs: ParagraphContent[];
      timestamp: number;
    }
    """

    prompt = f"""
    Given the following TypeScript interfaces:
    {typescript_schema}

    Overview:
    {overview}

    Table of contents:
    {tableOfContents}

    Write the required content for the point in the table of contents called {point} with {title} section returned as a json representation of a BodyResult.
    """
    
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format= { "type": "json_object" },
            messages=[
                {
                    "role": "system",
                    "content": "You are an API that generates paragraphs for a specific point of a digital document, using the overview and outline as a guide to infer what was already written. You adhere strictly to the Schema when responding."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
                
            ],
        )
        print("generated")
    except Exception as e:
        return {"error": str(e)}

    # Formatting the response to only include the generated text
    response_json = completion.choices[0].message.content
    # Returning the response in a JSON object format
    return response_json
