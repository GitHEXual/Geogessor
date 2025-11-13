using AutoMapper;
using ImageRecognitionAPI.Data.Repositories;
using ImageRecognitionAPI.Models.DTOs;
using ImageRecognitionAPI.Models.Enums;

namespace ImageRecognitionAPI.Services;

public class UserService : IUserService
{
    private readonly IUserRepository _userRepository;
    private readonly IMapper _mapper;

    public UserService(IUserRepository userRepository, IMapper mapper)
    {
        _userRepository = userRepository;
        _mapper = mapper;
    }

    public async Task<List<UserDto>> GetAllUsersAsync()
    {
        var users = await _userRepository.GetAllAsync();
        return _mapper.Map<List<UserDto>>(users);
    }

    public async Task<UserDto?> GetUserByIdAsync(Guid id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        return user == null ? null : _mapper.Map<UserDto>(user);
    }

    public async Task BanUserAsync(Guid id)
    {
        var result = await _userRepository.UpdateStatusAsync(id, UserStatus.Banned);
        if (!result)
            throw new KeyNotFoundException($"User with id {id} not found");
    }

    public async Task UnbanUserAsync(Guid id)
    {
        var result = await _userRepository.UpdateStatusAsync(id, UserStatus.Active);
        if (!result)
            throw new KeyNotFoundException($"User with id {id} not found");
    }

    public async Task DeleteUserAsync(Guid id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
            throw new KeyNotFoundException($"User with id {id} not found");

        await _userRepository.DeleteAsync(id);
    }
}



