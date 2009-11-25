boxee.setDefaultCrop(0,0,0,35);

if(boxee.getVersion() > 1.8)
{
  boxee.setCanPause(true);
}

boxee.onPlay = function()
{
	boxee.runInBrowser('document.getElementById("player").Content.ScriptableMembers.PlayVideo();');
}

boxee.onPause = function()
{
	boxee.runInBrowser('document.getElementById("player").Content.ScriptableMembers.PauseVideo();');
}

