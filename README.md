### **Detailed Steps and Process for Invoking Foundational LLM Models in Amazon Bedrock**
![image](https://github.com/user-attachments/assets/3bf42234-93d7-4dff-9d10-a76c15997027)

This guide provides a step-by-step explanation of the Python code and process I developed for invoking foundational LLM models via Amazon Bedrock, generating a blog, and storing the result in Amazon S3. Additionally, it explains how to use an API Gateway endpoint to invoke this functionality as a POST request.

---

### **1. Overview of the Code Workflow**

The Lambda function I created consists of three primary components:
1. **Blog Generation**:
   - Uses Amazon Bedrock's foundational LLMs to generate a blog based on a topic provided in the input.
2. **Saving Output to S3**:
   - Stores the generated blog in an Amazon S3 bucket as a text file.
3. **API Gateway Integration**:
   - Exposes the Lambda function as an HTTP endpoint to be invoked via POST requests.

---

### **2. Steps to Invoke Foundational Models**

#### **Step 1: Set Up the Bedrock Client**
Using the `boto3` library, I created a client to interact with Amazon Bedrock's runtime environment. The `bedrock-runtime` client is initialized with:
- **Region Name**: Specifies the AWS region (e.g., `us-east-2`).
- **Timeouts and Retries**: Configured using `botocore.config.Config` to handle potential request delays or failures.

Code snippet:
```python
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2",
                       config=botocore.config.Config(read_timeout=300, retries={'max_attempts': 3}))
```

---

#### **Step 2: Prepare the Input Payload**
To generate a blog, I designed an NLP prompt dynamically based on the user-provided topic. This prompt instructs the LLM to produce a 200-word blog.

- **Prompt Structure**:
  - The prompt uses a specific syntax (`<s>[INST]...[/INST]`) to guide the foundational model.
- **Additional Parameters**:
  - `max_gen_len`: Limits the maximum length of the generated output.
  - `temperature`: Controls randomness in the generation (lower values produce more deterministic results).
  - `top_p`: Implements nucleus sampling to refine generation quality.

Example Payload:
```python
body = {
    "prompt": "<s>[INST]Human: Write a 200 words blog on the topic What is Diffusion Model and GANs\nAssistant:[/INST]",
    "max_gen_len": 512,
    "temperature": 0.5,
    "top_p": 0.9
}
```

---

#### **Step 3: Invoke the Model**
I used the `invoke_model` method to send the request to Amazon Bedrock. It requires:
- **Model Identifier (`modelId`)**:
  - Specifies the foundational model to invoke (e.g., the ARN of the associated inference profile).
- **Input Payload**:
  - Contains the prompt and generation parameters.

Code snippet:
```python
response = bedrock.invoke_model(
    body=json.dumps(body),
    modelId= UPDATED_THIS_WITH_AWS_BEDROCK_MODEL
)
```
![image](https://github.com/user-attachments/assets/2fdbd343-3633-4cdc-8c63-f376e4416c95)

#### **Step 4: Extract the Generated Output**
The response from Bedrock contains the model's generated output in the `body` attribute. I processed this to extract the content as JSON.

Code snippet:
```python
response_content = response.get('body').read()
response_data = json.loads(response_content)
generated_blog = response_data['generation']
```

---

### **3. Save the Generated Blog to Amazon S3**

I developed the `save_blog_in_s3` function to upload the generated blog to an S3 bucket:
- **S3 Object Key**:
  - Dynamically constructed using the blog topic and a timestamp.
- **Bucket Name**:
  - The destination bucket for storing the blog.

Code snippet:
```python
s3_key = f"blog_output/{current_time}_{blog_topic}.txt"
s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generated_blog)
```

---

### **4. API Gateway Integration**

To enable external invocation, I integrated the Lambda function with API Gateway to expose it as a public HTTP endpoint. This allows external clients to invoke the function using a POST request.

1. **Create an API Gateway**:
   - I navigated to the AWS Management Console.
   - Created a new **HTTP API** and connected it to the Lambda function.
   - Deployed the API and noted the generated endpoint URL.

2. **Invoke the API**:
   - I tested the endpoint using tools like Postman, cURL, and custom scripts to send POST requests to the API Gateway endpoint.
   - ![image](https://github.com/user-attachments/assets/a7655611-6cb1-4bff-817a-732e2eba86a9)


Example POST request:
- **Endpoint**: `<API Gateway URL>`
- **Body**:
   ```json
   {
       "blog_topic": "What is Diffusion Model and GANs"
   }
   ```

---

### **5. Testing in Postman**

1. **Configure the POST Request**:
   - **URL**: Use the API Gateway URL provided in the AWS Console.
   - **Method**: POST.
   - **Headers**: Set `Content-Type` to `application/json`.
   - **Body**: Provide the JSON payload:
     ```json
     {
         "blog_topic": "What is Diffusion Model and GANs"
     }
     ```

2. **Send the Request**:
   - Once sent, the Lambda function generates the blog and saves it to S3.
   - The API response confirms completion:
     ```json
     {
         "statusCode": 200,
         "body": "Blog Generation is Completed!"
     }
     ```

---

### **Summary**

I created this project to automate blog generation using Amazon Bedrock's LLM capabilities, integrating them with S3 for storage and API Gateway for external invocation. Users can trigger the process via API Gateway by sending a POST request with the desired blog topic. For example, a POST request to the API Gateway with the payload:
```json
{
   "blog_topic": "What is Diffusion Model and GANs"
}
```
invokes the Lambda function to generate a blog, stores it in S3, and returns a confirmation message.

