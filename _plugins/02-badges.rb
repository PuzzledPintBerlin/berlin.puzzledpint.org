require 'jekyll'
require 'jekyll/utils'
require 'digest/sha1'

def longest_common_subarray(all_events, team_events)
  max_length = 0

  team_events_hash = {}
  team_events.each { |x| team_events_hash[x] = true }

  current_length = 0

  all_events.each do |element|
    if team_events_hash[element]
      current_length += 1
      max_length = [max_length, current_length].max
    else
      current_length = 0
    end
  end

  max_length
end


Jekyll::Hooks.register :site, :post_read do |site|
    def event_badges(site, result, x = false)
        date = result['event']
        badges = []
        badges.concat(site.data['event_mapping'][date]['badges'] || [])
        if result['solved']and result['duration'] < 3600
            badges << 'sub-1h'
        end
        badges
    end

    site.data['badge_mapping'] = {}

    site.data['badges'].each do |b|
        site.data['badge_mapping'][b['id']] = b
    end

    site.data['teams'].each do |team|
        team['results'].each do |result|
            b = event_badges(site,result)
            
            team['badges'].concat(b) if b.size > 0
            team['badges'].uniq!
        end

        x = team['results'].map {|x| x['event']}
        y = site.data['events'].map {|x| x['date'].to_s}
        team['streak'] = longest_common_subarray(y, x)
    end
end