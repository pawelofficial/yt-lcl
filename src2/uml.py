

#
#
#
#
#   ytd.download_vid
#        - downloads vid to tmp 
#   ytd.download_subs
#        - downloads subs to tmp 
#     
#   tts.parse_subs
#        - parses subs to csv 
#        - aggregates subs csv 
#   tts.translate
#       - translates subs csv 
#   tts.text_to_spech
#       - makes speech files from subs csv, saves them to /tmp/vids 
#   tts.trim_vid
#       - trims a video to timestamps 
#   tts.join_audios
#       - joins audios together 
#   tts.join_audio_video
#       - joins audio with a video 
#
# feature1 
#   wiz.workflow1()
#       - workflow1 -> download url -> do text to speech
#           -> download vid and subs  (url)                     -> vid_fp,subs_fp 
#           -> translate and agg      (src lng, tgt lag )       -> tr_df
#           -> text_to_speech         ()                        -> tr_df* [+fname]
#           -> trim_video             (ltrim, righttrim)        -> ()
#           -> join_audios            (tr_df)                   -> joined_audio_fp
#           -> join_audio_and_video   (vid_fp,joined_audio_fp)  -> tr_vid_fp 
#           -> cleanup temp 
#
# to do:  
#   - upload to channel
#   - observe a channel - loop things 
#
#
