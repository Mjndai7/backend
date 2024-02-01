class ResponseMessages:
    INVALID_DATA = "Invalid request Data!"
    CREATE_FUTURE_SLOTS = "You have attempted to create a slot before!"
    CONFLICTING_SLOT = "Cannot create this slot as it conflicts with an exisiting slot between {} and {}."
    CALENDAR_SLOT_NOT_FOUND = "Requested Calendar slot not found!"
    USER_NOT_FOUND = "The requested User ID does not exist, Please check again!"
    CALENDAR_SLOT_ALREADY_BOOKED = "The requested Calendar slot is already booked, kindly try booking another slot!"
    MISSING_KEY = "Missing key '{}' in the request!"
    REGISTRATION_REQUIRED = "You must be an Authenticated User to perform this activity!"
    BOOKING_NOT_FOUND = "The booking for the requested slot not found!"


