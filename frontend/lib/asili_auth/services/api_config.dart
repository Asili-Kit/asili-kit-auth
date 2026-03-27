class ApiConfig {
  static const String environment = String.fromEnvironment(
    "ASILI_ENV",
    defaultValue: "dev",
  );

  static const String _rawBaseUrl = String.fromEnvironment(
    "ASILI_API_BASE_URL",
    defaultValue: "http://172.20.10.2:8000",
  );

  static String get baseUrl {
    if (_rawBaseUrl.endsWith("/")) {
      return _rawBaseUrl.substring(0, _rawBaseUrl.length - 1);
    }
    return _rawBaseUrl;
  }
}
