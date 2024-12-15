import asyncio
import json
import httpx

async def test_add_todo():
    # Test cases with different scenarios
    test_cases = [
        {
            "name": "Valid todo with all fields",
            "input": {
                "task": "Test task",
                "when": "today",
                "description": "This is a test description"
            },
            "should_succeed": True
        }
    ]

    # Load environment variables
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    NOTION_API_KEY = os.getenv("NOTION_API_KEY")
    DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    NOTION_VERSION = "2022-06-28"
    NOTION_BASE_URL = "https://api.notion.com/v1"
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

    # Run tests
    async with httpx.AsyncClient() as client:
        for test_case in test_cases:
            print(f"\nRunning test: {test_case['name']}")
            try:
                # Prepare the request payload
                payload = {
                    "parent": {"database_id": DATABASE_ID},
                    "properties": {
                        "Task": {
                            "type": "title",
                            "title": [{"type": "text", "text": {"content": test_case["input"].get("task", "")}}]
                        },
                        "When": {
                            "type": "select",
                            "select": {"name": test_case["input"].get("when", "")}
                        },
                        "Checkbox": {
                            "type": "checkbox",
                            "checkbox": False
                        }
                    }
                }

                # Add description if present
                if "description" in test_case["input"]:
                    payload["properties"]["Description"] = {
                        "type": "rich_text",
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": test_case["input"]["description"]
                                }
                            }
                        ]
                    }

                # Print request payload for debugging
                print(f"Request payload: {json.dumps(payload, indent=2)}")

                response = await client.post(
                    f"{NOTION_BASE_URL}/pages",
                    headers=headers,
                    json=payload
                )
                
                # Print response for debugging
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")

                if test_case["should_succeed"]:
                    assert response.status_code in [200, 201], f"Expected success but got {response.status_code}"
                    print("✅ Test passed")
                else:
                    if response.status_code >= 400:
                        print("✅ Test passed (expected failure)")
                    else:
                        print("❌ Test failed - Expected failure but got success")
                    
            except httpx.HTTPError as e:
                if test_case["should_succeed"]:
                    print(f"❌ Test failed - HTTP Error: {str(e)}")
                else:
                    print("✅ Test passed (expected failure)")
            except AssertionError as e:
                print(f"❌ Test failed - {str(e)}")
            except Exception as e:
                print(f"❌ Test failed with unexpected error: {str(e)}")
                print(f"Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_add_todo())