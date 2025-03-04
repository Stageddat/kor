import discord


async def builder_request_panel_callback(
    button: discord.ui.Button, interaction: discord.Interaction, builder_type
):
    shutDownEmbed = discord.Embed(
        title="Service not currently available",
        description="The ticket system has been disabled indefinitely until further notice. We apologize for the inconvenience.\nNew tickets cannot be opened and open tickets will be closed over time.",
        colour=discord.Colour(int("ff0000", 16)),
    )
    await interaction.respond(embeds=[shutDownEmbed], ephemeral=True)
    return