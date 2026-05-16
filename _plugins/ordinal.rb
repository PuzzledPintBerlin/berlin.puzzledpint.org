module Jekyll
  module Ordinal
    def ordinal(n)
      return case n % 100
      when 11, 12, 13 then 'th'
      else 
        case n % 10
        when 1 then 'st'
        when 2 then 'nd'
        when 3 then 'rd'
        else 'th'
        end
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::Ordinal)