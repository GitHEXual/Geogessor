using ImageRecognitionAPI.Models.DTOs;
using ImageRecognitionAPI.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ImageRecognitionAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize(Roles = "Admin")]
public class AdminController : ControllerBase
{
    private readonly IUserService _userService;

    public AdminController(IUserService userService)
    {
        _userService = userService;
    }

    [HttpGet("users")]
    public async Task<ActionResult<List<UserDto>>> GetAllUsers()
    {
        var users = await _userService.GetAllUsersAsync();
        return Ok(users);
    }

    [HttpPost("users/{id}/ban")]
    public async Task<ActionResult> BanUser(Guid id)
    {
        await _userService.BanUserAsync(id);
        return NoContent();
    }

    [HttpPost("users/{id}/unban")]
    public async Task<ActionResult> UnbanUser(Guid id)
    {
        await _userService.UnbanUserAsync(id);
        return NoContent();
    }

    [HttpDelete("users/{id}")]
    public async Task<ActionResult> DeleteUser(Guid id)
    {
        await _userService.DeleteUserAsync(id);
        return NoContent();
    }
}



