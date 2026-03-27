class User {
  final int id;
  final String email;
  final bool isActive;
  final bool isSuperuser;
  final DateTime createdAt;

  User({
    required this.id,
    required this.email,
    required this.isActive,
    required this.isSuperuser,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      isActive: json['is_active'],
      isSuperuser: json['is_superuser'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
