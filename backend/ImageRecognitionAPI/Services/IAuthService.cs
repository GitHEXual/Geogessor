using ImageRecognitionAPI.Models.DTOs;

namespace ImageRecognitionAPI.Services;

public interface IAuthService
{
    Task<AuthResponse?> RegisterAsync(RegisterRequest request);
    Task<AuthResponse?> LoginAsync(LoginRequest request);
    string GenerateJwtToken(Guid userId, string email, string role);
}



