using ImageRecognitionAPI.Helpers;
using ImageRecognitionAPI.Models.DTOs;
using ImageRecognitionAPI.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ImageRecognitionAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;

    public UsersController(IUserService userService)
    {
        _userService = userService;
    }

    [HttpGet("me")]
    public async Task<ActionResult<UserDto>> GetCurrentUser()
    {
        var userId = ClaimsHelper.GetUserId(User);
        if (userId == null)
            return Unauthorized(new { message = "Invalid user token" });

        var user = await _userService.GetUserByIdAsync(userId.Value);
        if (user == null)
            return NotFound();

        return Ok(user);
    }

    [HttpDelete("me")]
    public async Task<ActionResult> DeleteOwnAccount()
    {
        var userId = ClaimsHelper.GetUserId(User);
        if (userId == null)
            return Unauthorized(new { message = "Invalid user token" });

        await _userService.DeleteUserAsync(userId.Value);
        return NoContent();
    }
}



