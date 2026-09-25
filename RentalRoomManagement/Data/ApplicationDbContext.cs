using Microsoft.EntityFrameworkCore;
using RentalRoomManagement.Models;

namespace RentalRoomManagement.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<Room> Rooms { get; set; }
    }
}