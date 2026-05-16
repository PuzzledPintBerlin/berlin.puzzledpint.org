require 'jekyll'
require 'jekyll/utils'
require 'digest/sha1'

Jekyll::Hooks.register :site, :post_read do |site|
    def find_alias_or_slug(site, team_name, event = nil)
        tn = team_name.gsub('β', 'beta')
        tn = tn.gsub('²', 'squared')
        slug = Jekyll::Utils.slugify(tn)

        # Find alias using first matching entry in 'aliases'
        # in case the csv contains a event date, then the alias is limited to a single event
        # so only trigger it for a matching event
        aliased = site.data['aliases'].find do |row|
            (row['event'] == event && row['name'] == slug) || row['name'] == slug
        end

        aliased&.[]('slug') || slug
    end

    site.data['teams'] = {}
    site.data['event_mapping'] = {}

    site.data['results'].each do |row|
        next if row['Team Name'].empty?

        row['duration'] = nil
        row['solved'] = false
        row['slug'] = find_alias_or_slug(site, row['Team Name'], row['Date'])
        row['color_index'] = Digest::SHA1.hexdigest(row['slug']).to_i(16) % site.data['colors'].size

        site.data['teams'][row['slug']] ||= {
            'results' => [],
            'badges' => [],
            'slug' => row['slug'],
            'color_index'=> row['color_index'],
            'name' => row['Team Name']
        }

        # if the slug matches the generated one, then update team name
        # since the above only sets it based on the ordering of results

        if row['slug'] == Jekyll::Utils.slugify(row['Team Name'])
            site.data['teams'][row['slug']]['name'] = row['Team Name']
        end

        unless row['End Time'].nil?
            row['solved'] = true
            row['duration'] = (Time.parse(row['End Time']).to_i - Time.parse(row['Start Time']).to_i)
        end

        site.data['teams'][row['slug']]['results'] << {
            'duration' => row['duration'],
            'players' => row['Team Size'],
            'event' => row['Date'],
            'solved' => row['solved'],
        }
    end

    site.data['results'].sort_by! do |r|
        [r['solved'] ? 0 : 1, r['duration'], r['Start Time']]
    end
    
    # Add rank to each team
    # and map event date to theme

    site.data['events'].each do |event|
        date = event['date'].to_s
        site.data['event_mapping'][date] = event

        event_results = site.data['results'].select {|r| r['Date'] == date}
        event_results.each_with_index do |result, idx|
            slug = result['slug']
            site.data['teams'][slug]['results'].each do |r|
                r['rank'] = idx+1 if r['event'] == date
            end
        end
    end

    # Award the has-alias badge
    site.data['aliases'].each do |row|
        slug = row['slug']
        site.data['teams'][slug]['badges'] << 'has-alias'
    end

    # Convert hash to array
    site.data['teams'] = site.data['teams'].values
    # Sort by no of appearances
    site.data['teams'].sort_by! {|r| -r['results'].size }
end