using ImageRecognitionAPI.Helpers;
using ImageRecognitionAPI.Models.DTOs;
using ImageRecognitionAPI.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ImageRecognitionAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ImagesController : ControllerBase
{
    private readonly IImageService _imageService;

    public ImagesController(IImageService imageService)
    {
        _imageService = imageService;
    }

    private Guid GetCurrentUserId()
    {
        var userId = ClaimsHelper.GetUserId(User);
        if (userId == null)
            throw new UnauthorizedAccessException("Invalid user token");
        return userId.Value;
    }

    [HttpPost("upload")]
    public async Task<ActionResult<ImageDto>> UploadImage([FromForm] IFormFile file)
    {
        if (file == null)
            return BadRequest(new { message = "File is required" });

        var userId = GetCurrentUserId();
        var result = await _imageService.UploadImageAsync(userId, file);

        return CreatedAtAction(nameof(GetImage), new { id = result.Id }, result);
    }

    [HttpGet]
    public async Task<ActionResult<List<ImageDto>>> GetMyImages()
    {
        var userId = GetCurrentUserId();
        var images = await _imageService.GetUserImagesAsync(userId);
        return Ok(images);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<ImageDto>> GetImage(Guid id)
    {
        var image = await _imageService.GetImageByIdAsync(id);
        if (image == null)
            return NotFound();

        return Ok(image);
    }

    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteImage(Guid id)
    {
        var userId = GetCurrentUserId();
        await _imageService.DeleteImageAsync(id, userId);
        return NoContent();
    }

    [HttpGet("{id}/download")]
    public async Task<ActionResult> DownloadImage(Guid id)
    {
        var userId = GetCurrentUserId();
        var stream = await _imageService.DownloadImageAsync(id, userId);
        var image = await _imageService.GetImageByIdAsync(id);
        return File(stream, image!.ContentType, image.FileName);
    }
}



