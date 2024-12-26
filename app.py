import boto3 # this is used to invoke the Foundational Models
import botocore.config 
import json
from datetime import datetime


# Creating a blog
def blog_generate_using_bedrock(blog_topic: str)->str:
    prompt = f"""
                <s>[INST]Human: Write a 200 words blog on the topic {blog_topic}
                Assistant:[/INST]
            """
    
    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        bedrock = boto3.client("bedrock-runtime", region_name = "us-east-2",
                               config = botocore.config.Config(read_timeout=300, retries={'max_attempts':3}))
    
        response = bedrock.invoke_model(
                        body=json.dumps(body),
                        modelId= "arn:aws:bedrock:us-east-2:677276104961:inference-profile/us.meta.llama3-1-8b-instruct-v1:0", 
                        #"meta.llama3-1-8b-instruct-v1:0",
                       # inferenceArn="arn:aws:bedrock:us-east-2:677276104961:inference-profile/us.meta.llama3-1-8b-instruct-v1:0"
                        )

        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)

        blog_details = response_data['generation']
        return blog_details
    
    except Exception as e:
        print(f"Error Generated : {e}")
        return ""
    

def save_blog_in_s3(s3_key, s3_bucket, generated_blog):
    s3 = boto3.client("s3")
    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = generated_blog)
    except Exception as e:
        print(f"Issue raised while saving the blog to Bucket. Error: {e}")


def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event['body'])   
    blog_topic = event['blog_topic']

    generated_blog = blog_generate_using_bedrock(blog_topic = blog_topic)

    if generated_blog:
        # Saving the above generated response in the S3 bucket as txt file
        current_time = datetime.now().strftime("%H%M%S")
        s3_key = f"blog_output/{current_time}_{blog_topic}.txt" 
        s3_bucket = "aws-bedrock-s3-bucket"
        save_blog_in_s3(s3_key, s3_bucket, generated_blog)
    else:
        print("No response is generated..")

    return {
        'statusCode':200,
        'body':json.dumps("Blog Generation is Completed !")
    }
