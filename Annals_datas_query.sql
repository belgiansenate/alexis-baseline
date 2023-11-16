select
 h.handelingenid, h.datum, h.legislatuur, h.nummer, h.tijdstip_fr, h.beginblz, h.eindblz, 
 p.pdfid
from handelingen h, publicatie p
where h.handelingenid = p.handelingenid
and h.legislatuur >= 2
order by 3,4;