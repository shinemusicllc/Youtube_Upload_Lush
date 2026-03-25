using BaseSource.Data.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace BaseSource.Data.Configurations
{
    public class UserChannelConfiguration : IEntityTypeConfiguration<UserChannel>
    {
        public void Configure(EntityTypeBuilder<UserChannel> builder)
        {
            builder.ToTable("UserChannels");

            builder.HasKey(x => x.Id);

            builder.HasOne(x => x.ChannelYoutube).WithMany(x => x.UserChannels).HasForeignKey(x => x.ChannelYoutubeId);
            builder.HasOne(x => x.AppUser).WithMany(x => x.UserChannels).HasForeignKey(x => x.UserId);
        }
    }
}
