using ImageRecognitionAPI.Models.Entities;
using ImageRecognitionAPI.Models.Enums;

namespace ImageRecognitionAPI.Data.Repositories;

public interface IUserRepository
{
    Task<User?> GetByIdAsync(Guid id);
    Task<User?> GetByEmailAsync(string email);
    Task<List<User>> GetAllAsync();
    Task<User> CreateAsync(User user);
    Task UpdateAsync(User user);
    Task DeleteAsync(Guid id);
    Task<bool> EmailExistsAsync(string email);
    Task<bool> UpdateStatusAsync(Guid id, UserStatus status);
}



