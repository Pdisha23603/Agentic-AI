{
  "name": "trackOrder",
  "description": "Tracks the status of a food delivery order.",
  "parameters": {
    "type": "object",
    "properties": {
      "order_id": {
        "type": "string",
        "description": "Unique order ID of the food delivery."
      },
      "user_phone": {
        "type": "string",
        "description": "Registered phone number of the customer."
      }
    },
    "required": ["order_id", "user_phone"]
  }
}