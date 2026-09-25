using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations;

namespace RentalRoomManagement.Models
{
    public class Room
    {
        public int Id { get; set; }

        [Required]
        public string RoomCode { get; set; } = string.Empty;

        public string? Description { get; set; }

        public string? Image { get; set; }

        [Required]
        public string RoomType { get; set; } = string.Empty;

        [Required]
        [Precision(18, 2)]
        public decimal Price { get; set; }

        [Required]
        public string Status { get; set; } = "Trống";
    }
}