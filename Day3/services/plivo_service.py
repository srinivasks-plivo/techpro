"""
Plivo Service - Generates XML responses for Plivo Voice API.

WHY PLIVO XML?
===============
Plivo doesn't execute Python code directly during calls.
Instead, it:
1. Makes a webhook request to our server
2. We respond with XML instructions
3. Plivo executes those instructions (speak, wait for input, transfer, etc.)

THE BIG PICTURE:
=================
When Plivo calls us, we respond with XML that tells it what to do:

<Response>
  <Speak>Welcome to our IVR. Press 1 for Sales...</Speak>
  <GetDigits action="/webhooks/input" timeout="5" numDigits="1" />
</Response>

PLIVO XML ELEMENTS:
===================
<Speak>             = Text-to-speech: say something to caller
<GetDigits>         = Wait for digit input, then call action URL
<Play>              = Play audio file
<Dial>              = Transfer call to number
<Redirect>          = Send call to different URL for new instructions
<Hangup>            = End the call
<Wait>              = Silence/waiting period

FLOW:
  Plivo calls /webhooks/answer
    ↓
  We call plivo_service.generate_menu_xml()
    ↓
  We return XML with <Speak> and <GetDigits>
    ↓
  Plivo speaks message to caller
    ↓
  Caller presses digit
    ↓
  Plivo calls /webhooks/input with the digit
"""

from config import get_config

# Get configuration
config = get_config()


class PlivoXMLService:
    """
    Generate Plivo XML responses.

    Plivo uses XML to control voice calls. This service
    builds the XML strings that tell Plivo what to do.
    """

    @staticmethod
    def generate_menu_xml(message, timeout=None, max_digits=None, action_url="/voice/input"):
        """
        Generate XML for a menu screen.

        This creates a response that:
        1. Says a message to the caller (using text-to-speech)
        2. Waits for them to press digits
        3. Sends those digits to action_url

        Args:
            message (str): What to say to the caller via TTS
            timeout (int): Seconds to wait for input (default: config.DEFAULT_TIMEOUT)
            max_digits (int): How many digits to accept (default: 1)
            action_url (str): Where to send the digits (default: /webhooks/input)

        Returns:
            str: XML response string

        Example:
            xml = plivo_service.generate_menu_xml(
                message="Press 1 for Sales, 2 for Support",
                timeout=5,
                max_digits=1,
                action_url="/webhooks/input"
            )
            # Returns:
            # <Response>
            #   <GetDigits action="/webhooks/input" timeout="5" numDigits="1">
            #     <Speak>Press 1 for Sales, 2 for Support</Speak>
            #   </GetDigits>
            # </Response>
        """
        # Use defaults from config if not provided
        if timeout is None:
            timeout = config.DEFAULT_TIMEOUT
        if max_digits is None:
            max_digits = 1

        # Build XML
        xml = (
            '<Response>\n'
            f'  <GetDigits action="{action_url}" timeout="{timeout}" numDigits="{max_digits}">\n'
            f'    <Speak>{PlivoXMLService._escape_xml(message)}</Speak>\n'
            '  </GetDigits>\n'
            '</Response>'
        )

        print(f"🎵 Generated menu XML for: {message[:50]}...")
        return xml

    @staticmethod
    def generate_speak_only_xml(message):
        """
        Generate XML to just speak a message (no input waiting).

        Use this for informational messages like:
        - "Please hold while we transfer you"
        - "Thank you for calling, goodbye"

        Args:
            message (str): What to say

        Returns:
            str: XML response

        Example:
            xml = plivo_service.generate_speak_only_xml(
                "Thank you for calling. Goodbye."
            )
        """
        xml = (
            '<Response>\n'
            f'  <Speak>{PlivoXMLService._escape_xml(message)}</Speak>\n'
            '</Response>'
        )

        print(f"🎵 Generated speak-only XML")
        return xml

    @staticmethod
    def generate_transfer_xml(phone_number, timeout=30):
        """
        Generate XML to transfer the call to a phone number.

        This tells Plivo to hang up on our server and
        dial the specified phone number instead.

        Args:
            phone_number (str): Where to transfer (e.g., "+15551234567")
            timeout (int): Seconds to ring before giving up

        Returns:
            str: XML response

        Example:
            xml = plivo_service.generate_transfer_xml(
                phone_number="+15551234567",
                timeout=30
            )
            # Returns:
            # <Response>
            #   <Dial timeout="30">
            #     <Number>+15551234567</Number>
            #   </Dial>
            # </Response>
        """
        xml = (
            '<Response>\n'
            f'  <Dial timeout="{timeout}">\n'
            f'    <Number>{phone_number}</Number>\n'
            '  </Dial>\n'
            '</Response>'
        )

        print(f"📞 Generated transfer XML to: {phone_number}")
        return xml

    @staticmethod
    def generate_hangup_xml(message=None):
        """
        Generate XML to end the call.

        Optionally says something before hanging up.

        Args:
            message (str): Optional message to say before hanging up

        Returns:
            str: XML response

        Example:
            # Hang up immediately
            xml = plivo_service.generate_hangup_xml()

            # Say goodbye then hang up
            xml = plivo_service.generate_hangup_xml(
                "Thank you for calling. Goodbye!"
            )
        """
        if message:
            xml = (
                '<Response>\n'
                f'  <Speak>{PlivoXMLService._escape_xml(message)}</Speak>\n'
                '  <Hangup />\n'
                '</Response>'
            )
        else:
            xml = (
                '<Response>\n'
                '  <Hangup />\n'
                '</Response>'
            )

        print("📵 Generated hangup XML")
        return xml

    @staticmethod
    def generate_play_xml(audio_url, action_url="/voice/input"):
        """
        Generate XML to play a pre-recorded audio file.

        Instead of text-to-speech, this plays an actual audio file.

        Args:
            audio_url (str): URL to audio file (e.g., "https://example.com/menu.mp3")
            action_url (str): Where to send digits (default: /webhooks/input)

        Returns:
            str: XML response

        Example:
            xml = plivo_service.generate_play_xml(
                audio_url="https://example.com/welcome.mp3",
                action_url="/webhooks/input"
            )
        """
        xml = (
            '<Response>\n'
            f'  <GetDigits action="{action_url}" timeout="{config.DEFAULT_TIMEOUT}" numDigits="1">\n'
            f'    <Play>{audio_url}</Play>\n'
            '  </GetDigits>\n'
            '</Response>'
        )

        print(f"🎵 Generated play XML for: {audio_url}")
        return xml

    @staticmethod
    def generate_wait_xml(duration=1):
        """
        Generate XML to add silence/waiting period.

        Useful if you need a pause between messages.

        Args:
            duration (int): Seconds to wait

        Returns:
            str: XML response

        Example:
            xml = plivo_service.generate_wait_xml(duration=2)
        """
        xml = (
            '<Response>\n'
            f'  <Wait length="{duration}" />\n'
            '</Response>'
        )

        print(f"⏳ Generated wait XML ({duration}s)")
        return xml

    @staticmethod
    def generate_redirect_xml(redirect_url):
        """
        Generate XML to redirect call to a different URL.

        This tells Plivo to call a different URL for new instructions.

        Args:
            redirect_url (str): URL to redirect to (e.g., "/webhooks/custom")

        Returns:
            str: XML response

        Example:
            xml = plivo_service.generate_redirect_xml("/webhooks/advanced_menu")
        """
        xml = (
            '<Response>\n'
            f'  <Redirect>{redirect_url}</Redirect>\n'
            '</Response>'
        )

        print(f"🔄 Generated redirect XML to: {redirect_url}")
        return xml

    @staticmethod
    def generate_invalid_input_xml(retry_count=None, max_retries=None):
        """
        Generate XML for when user presses invalid digit.

        Args:
            retry_count (int): How many times have they tried? (for messages)
            max_retries (int): Max allowed attempts before error

        Returns:
            str: XML response

        Example:
            xml = plivo_service.generate_invalid_input_xml(
                retry_count=1,
                max_retries=3
            )
        """
        if max_retries is None:
            max_retries = config.MAX_RETRIES

        if retry_count and retry_count >= max_retries:
            message = "I didn't understand that. Your call is being transferred."
            xml = PlivoXMLService.generate_speak_only_xml(message)
        else:
            message = "Invalid input. Please try again."
            xml = PlivoXMLService.generate_speak_only_xml(message)

        print("❌ Generated invalid input XML")
        return xml

    @staticmethod
    def generate_timeout_xml(retry_count=None, max_retries=None):
        """
        Generate XML for when user doesn't press anything (timeout).

        Args:
            retry_count (int): How many times have they timed out?
            max_retries (int): Max allowed before error

        Returns:
            str: XML response

        Example:
            xml = plivo_service.generate_timeout_xml(
                retry_count=1,
                max_retries=3
            )
        """
        if max_retries is None:
            max_retries = config.MAX_RETRIES

        if retry_count and retry_count >= max_retries:
            message = "We didn't hear from you. Your call is being transferred."
            xml = PlivoXMLService.generate_speak_only_xml(message)
        else:
            message = "We didn't hear you. Please try again."
            xml = PlivoXMLService.generate_speak_only_xml(message)

        print("⏱️  Generated timeout XML")
        return xml

    # ===== HELPER METHODS =====

    @staticmethod
    def _escape_xml(text):
        """
        Escape special characters in text for XML.

        XML has reserved characters: < > & " '
        We need to escape them so they don't break the XML.

        Args:
            text (str): Raw text

        Returns:
            str: XML-safe text

        Example:
            text = 'Press 1 & "confirm"'
            escaped = _escape_xml(text)
            # Returns: 'Press 1 &amp; &quot;confirm&quot;'
        """
        replacements = {
            "&": "&amp;",  # Must be first!
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&apos;",
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text

    @staticmethod
    def validate_xml(xml_string):
        """
        Basic validation that XML looks correct.

        Args:
            xml_string (str): XML to validate

        Returns:
            bool: True if valid structure, False otherwise

        Example:
            if plivo_service.validate_xml(xml):
                print("XML is valid!")
        """
        # Check for required Response tags
        if not xml_string.startswith("<Response>"):
            return False
        if not xml_string.rstrip().endswith("</Response>"):
            return False
        return True


# ===== SINGLETON INSTANCE =====
plivo_service = PlivoXMLService()


# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    """
    Example: How to use Plivo service

    Shows different types of XML responses.
    """

    print("=== MENU XML (most common) ===")
    xml = plivo_service.generate_menu_xml(
        "Welcome to our IVR. Press 1 for Sales, 2 for Support, 3 for Billing"
    )
    print(xml)
    print()

    print("=== TRANSFER XML ===")
    xml = plivo_service.generate_transfer_xml("+15551234567")
    print(xml)
    print()

    print("=== HANGUP XML ===")
    xml = plivo_service.generate_hangup_xml("Thank you for calling. Goodbye!")
    print(xml)
    print()

    print("=== INVALID INPUT XML ===")
    xml = plivo_service.generate_invalid_input_xml(retry_count=1, max_retries=3)
    print(xml)
    print()

    print("=== TIMEOUT XML ===")
    xml = plivo_service.generate_timeout_xml(retry_count=2, max_retries=3)
    print(xml)
