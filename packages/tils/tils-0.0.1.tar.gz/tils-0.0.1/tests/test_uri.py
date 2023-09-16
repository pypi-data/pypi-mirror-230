from tils.uri import uri_validator

def test_uri_validator():

    # arrange
    good_uris = [
        "http://www.google.com",
        "https://www.google.com",
        "ftp://www.google.com",
        "http://www.google.com:8080",
        "https://www.google.com:8080",
        "ftp://www.google.com:8080",
        "http://www.google.com:8080/path/to/file",
        "https://www.google.com:8080/path/to/file",
        "ftp://www.google.com:8080/path/to/file",
        "http://www.google.com:8080/path/to/file?query=string",
        "https://www.google.com:8080/path/to/file?query=string",
        "ftp://www.google.com:8080/path/to/file?query=string",
        "http://www.google.com:8080/path/to/file?query=string&another=string",
        "https://www.google.com:8080/path/to/file?query=string&another=string",
        "ftp://www.google.com:8080/path/to/file?query=string&another=string",
        "http://www.google.com:8080/path/to/file?query=string&another=string#fragment",
        "https://www.google.com:8080/path/to/file?query=string&another=string#fragment",
        "ftp://www.google.com:8080/path/to/file?query=string&another=string#fragment",
        "http://www.google.com:8080/path/to/file?query=string&another=string#fragment?another=fragment",
        "https://www.google.com:8080/path/to/file?query=string&another=string#fragment?another=fragment",
        "ftp://www.google.com:8080/path/to/file?query=string&another=string#fragment?another=fragment"
    ]

    bad_uris = [
        "",
        "http://",
        "https://",
        "ftp://",
        "google",
        ".com"
    ]

    # act
    for uri in good_uris:
        result = uri_validator(uri)

        # assert
        assert result == True

    for uri in bad_uris:
        result = uri_validator(uri)

        # assert
        assert result == False