using ImageRecognitionAPI.Models.DTOs;

namespace ImageRecognitionAPI.Services;

public interface IUserService
{
    Task<List<UserDto>> GetAllUsersAsync();
    Task<UserDto?> GetUserByIdAsync(Guid id);
    Task BanUserAsync(Guid id);
    Task UnbanUserAsync(Guid id);
    Task DeleteUserAsync(Guid id);
}



