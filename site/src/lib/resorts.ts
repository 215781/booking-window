// Club Med French Alps ski resorts tracked daily. `id` matches the price data.
export type CollectionKey = 'clubmed-ski' | 'clubmed-sun' | 'markwarner-sun';
export interface Resort {
  collection: CollectionKey; id: string; slug: string; name: string; fullName: string; area: string; altitude?: string;
  image?: string; imageAlt?: string; bookingUrl: string; blog?: string;
}

export const SKI: Resort[] = [
  { collection: 'clubmed-ski', id: 'tignes-val-claret', slug: 'tignes', name: 'Tignes', fullName: 'Club Med Tignes', area: "Espace Killy", altitude: '2,100m', image: 'Tignes', imageAlt: 'Snow-covered slopes above Tignes', bookingUrl: 'https://www.clubmed.co.uk/r/tignes/w', blog: 'best-time-to-book-club-med-tignes' },
  { collection: 'clubmed-ski', id: 'val-thorens', slug: 'val-thorens', name: 'Val Thorens', fullName: 'Club Med Val Thorens Sensations', area: 'Three Valleys', altitude: '2,300m', image: 'Val-Thorens', imageAlt: 'Val Thorens resort in winter', bookingUrl: 'https://www.clubmed.co.uk/r/val-thorens-sensations/y', blog: 'best-time-to-book-club-med-val-thorens' },
  { collection: 'clubmed-ski', id: 'val-disere', slug: 'val-disere', name: "Val d'Isère", fullName: "Club Med Val d'Isère", area: 'Espace Killy', altitude: '1,850m', image: 'Val-Disere', imageAlt: "Val d'Isère village under snow", bookingUrl: 'https://www.clubmed.co.uk/r/val-d-isere/w', blog: 'best-time-to-book-club-med-val-disere' },
  { collection: 'clubmed-ski', id: 'les-arcs', slug: 'les-arcs', name: 'Les Arcs', fullName: 'Club Med Les Arcs Panorama', area: 'Paradiski', altitude: '1,950m', image: 'Les-Arcs', imageAlt: 'Les Arcs ski area', bookingUrl: 'https://www.clubmed.co.uk/r/les-arcs-panorama/w', blog: 'best-time-to-book-club-med-les-arcs' },
  { collection: 'clubmed-ski', id: 'la-plagne-2100', slug: 'la-plagne', name: 'La Plagne', fullName: 'Club Med La Plagne 2100', area: 'Paradiski', altitude: '2,100m', image: 'La-plagne', imageAlt: 'La Plagne in winter', bookingUrl: 'https://www.clubmed.co.uk/r/la-plagne-2100/y', blog: 'best-time-to-book-club-med-la-plagne' },
  { collection: 'clubmed-ski', id: 'peisey-vallandry', slug: 'peisey-vallandry', name: 'Peisey-Vallandry', fullName: 'Club Med Peisey-Vallandry', area: 'Paradiski', altitude: '1,600m', image: 'Peisey-Vallandry', imageAlt: 'Peisey-Vallandry forest slopes', bookingUrl: 'https://www.clubmed.co.uk/r/peisey-vallandry/w', blog: 'best-time-to-book-club-med-peisey-vallandry' },
  { collection: 'clubmed-ski', id: 'alpe-dhuez', slug: 'alpe-dhuez', name: "Alpe d'Huez", fullName: "Club Med Alpe d'Huez", area: 'Oisans', altitude: '1,860m', image: 'Alpe-dhuez', imageAlt: "Alpe d'Huez ski slopes", bookingUrl: 'https://www.clubmed.co.uk/r/alpe-d-huez/w', blog: 'best-time-to-book-club-med-alpe-dhuez' },
  { collection: 'clubmed-ski', id: 'la-rosiere', slug: 'la-rosiere', name: 'La Rosière', fullName: 'Club Med La Rosière', area: 'Espace San Bernardo', altitude: '1,850m', image: 'La-Rosiere', imageAlt: 'La Rosière in winter', bookingUrl: 'https://www.clubmed.co.uk/r/la-rosiere/w', blog: 'best-time-to-book-club-med-la-rosiere' },
  { collection: 'clubmed-ski', id: 'valmorel', slug: 'valmorel', name: 'Valmorel', fullName: 'Club Med Valmorel', area: 'Grand Domaine', altitude: '1,460m', image: 'Valmorel', imageAlt: 'Valmorel resort and slopes', bookingUrl: 'https://www.clubmed.co.uk/r/valmorel/w', blog: 'best-time-to-book-club-med-valmorel' },
  { collection: 'clubmed-ski', id: 'grand-massif', slug: 'grand-massif', name: 'Grand Massif', fullName: 'Club Med Grand Massif Samoëns Morillon', area: 'Grand Massif', altitude: '', image: 'Grand-Massif', imageAlt: 'Grand Massif mountains', bookingUrl: 'https://www.clubmed.co.uk/r/grand-massif-samoens-morillon/w', blog: 'best-time-to-book-club-med-grand-massif' },
  { collection: 'clubmed-ski', id: 'serre-chevalier', slug: 'serre-chevalier', name: 'Serre-Chevalier', fullName: 'Club Med Serre-Chevalier', area: 'Southern Alps', altitude: '1,400m', image: 'Serre-chevalier', imageAlt: 'Serre-Chevalier valley in winter', bookingUrl: 'https://www.clubmed.co.uk/r/serre-chevalier/w', blog: 'best-time-to-book-club-med-serre-chevalier' },
];

export const SUN: Resort[] = [
  { collection: 'clubmed-sun', id: 'gregolimano', slug: 'gregolimano', name: "Gregolimano", fullName: "Club Med Gregolimano", area: "Halkidiki, Greece", bookingUrl: 'https://www.clubmed.co.uk/r/gregolimano/y', image: 'Gregolimano', imageAlt: "Gregolimano resort" },
  { collection: 'clubmed-sun', id: 'magna-marbella', slug: 'magna-marbella', name: "Magna Marbella", fullName: "Club Med Magna Marbella", area: "Costa del Sol, Spain", bookingUrl: 'https://www.clubmed.co.uk/r/magna-marbella/y', image: 'Magna-Marbella', imageAlt: "Magna Marbella resort" },
  { collection: 'clubmed-sun', id: 'da-balaia', slug: 'da-balaia', name: "Da Balaia", fullName: "Club Med Da Balaia", area: "Algarve, Portugal", bookingUrl: 'https://www.clubmed.co.uk/r/da-balaia/y', image: 'Da-Balaia', imageAlt: "Da Balaia resort" },
  { collection: 'clubmed-sun', id: 'la-caravelle', slug: 'la-caravelle', name: "La Caravelle", fullName: "Club Med La Caravelle", area: "Corsica, France", bookingUrl: 'https://www.clubmed.co.uk/r/la-caravelle/y', image: 'La-Caravelle', imageAlt: "La Caravelle resort" },
  { collection: 'clubmed-sun', id: 'la-palmyre-atlantique', slug: 'la-palmyre-atlantique', name: "La Palmyre Atlantique", fullName: "Club Med La Palmyre Atlantique", area: "Vendée, France", bookingUrl: 'https://www.clubmed.co.uk/r/la-palmyre-atlantique/y', image: 'La-Palmyre-Atlantique', imageAlt: "La Palmyre Atlantique resort" },
  // 'la-palmyre' (LPAC) hidden 1 Oct 2026: no clubmed.co.uk page exists; checker still collects it.
  { collection: 'clubmed-sun', id: 'la-palmeraie-marrakech', slug: 'la-palmeraie-marrakech', name: "La Palmeraie (Marrakech)", fullName: "Club Med La Palmeraie (Marrakech)", area: "Marrakech, Morocco", bookingUrl: 'https://www.clubmed.co.uk/r/marrakech-la-palmeraie/y', image: 'La-Palmeraie-Marrakech', imageAlt: "La Palmeraie (Marrakech) resort" },
  { collection: 'clubmed-sun', id: 'palmiye', slug: 'palmiye', name: "Palmiye", fullName: "Club Med Palmiye", area: "Antalya, Turkey", bookingUrl: 'https://www.clubmed.co.uk/r/palmiye/y', image: 'Palmiye', imageAlt: "Palmiye resort" },
  { collection: 'clubmed-sun', id: 'kani', slug: 'kani', name: "Kani", fullName: "Club Med Kani", area: "North Malé, Maldives", bookingUrl: 'https://www.clubmed.co.uk/r/kani/y', image: 'Kani', imageAlt: "Kani resort" },
  { collection: 'clubmed-sun', id: 'cefalu', slug: 'cefalu', name: "Cefalù", fullName: "Club Med Cefalù", area: "Sicily, Italy", bookingUrl: 'https://www.clubmed.co.uk/r/cefalu/y' },
  { collection: 'clubmed-sun', id: 'opio-en-provence', slug: 'opio-en-provence', name: "Opio en Provence", fullName: "Club Med Opio en Provence", area: "Provence, France", bookingUrl: 'https://www.clubmed.co.uk/r/opio-en-provence/y' },
  { collection: 'clubmed-sun', id: 'bodrum', slug: 'bodrum', name: "Bodrum", fullName: "Club Med Bodrum", area: "Bodrum, Turkey", bookingUrl: 'https://www.clubmed.co.uk/r/bodrum/y' },
  { collection: 'clubmed-sun', id: 'djerba-la-douce', slug: 'djerba-la-douce', name: "Djerba La Douce", fullName: "Club Med Djerba La Douce", area: "Djerba, Tunisia", bookingUrl: 'https://www.clubmed.co.uk/r/djerba-la-douce/y' },
  { collection: 'clubmed-sun', id: 'phuket', slug: 'phuket', name: "Phuket", fullName: "Club Med Phuket", area: "Phuket, Thailand", bookingUrl: 'https://www.clubmed.co.uk/r/phuket/y' },
  { collection: 'clubmed-sun', id: 'cherating-beach', slug: 'cherating-beach', name: "Cherating Beach", fullName: "Club Med Cherating Beach", area: "Pahang, Malaysia", bookingUrl: 'https://www.clubmed.co.uk/r/cherating-beach/y' },
  { collection: 'clubmed-sun', id: 'the-finolhu-villas', slug: 'the-finolhu-villas', name: "The Finolhu Villas", fullName: "Club Med The Finolhu Villas", area: "Baa Atoll, Maldives", bookingUrl: 'https://www.clubmed.co.uk/r/the-finolhu-villas/y' },
  { collection: 'clubmed-sun', id: 'la-plantation-d-albion', slug: 'la-plantation-d-albion', name: "La Plantation d'Albion", fullName: "Club Med La Plantation d'Albion", area: "Black River, Mauritius", bookingUrl: 'https://www.clubmed.co.uk/r/la-plantation-d-albion-club-med/y' },
  { collection: 'clubmed-sun', id: 'la-pointe-aux-canonniers', slug: 'la-pointe-aux-canonniers', name: "La Pointe aux Canonniers", fullName: "Club Med La Pointe aux Canonniers", area: "Grand Baie, Mauritius", bookingUrl: 'https://www.clubmed.co.uk/r/la-pointe-aux-canonniers/y' },
  { collection: 'clubmed-sun', id: 'seychelles', slug: 'seychelles', name: "Seychelles", fullName: "Club Med Seychelles", area: "Sainte Anne, Seychelles", bookingUrl: 'https://www.clubmed.co.uk/r/seychelles/y' },
  { collection: 'clubmed-sun', id: 'punta-cana', slug: 'punta-cana', name: "Punta Cana", fullName: "Club Med Punta Cana", area: "Punta Cana, Dominican Republic", bookingUrl: 'https://www.clubmed.co.uk/r/punta-cana/y' },
  { collection: 'clubmed-sun', id: 'cancun', slug: 'cancun', name: "Cancún", fullName: "Club Med Cancún", area: "Cancún, Mexico", bookingUrl: 'https://www.clubmed.co.uk/r/cancun/y' },
  { collection: 'clubmed-sun', id: 'miches-playa-esmeralda', slug: 'miches-playa-esmeralda', name: "Michès Playa Esmeralda", fullName: "Club Med Michès Playa Esmeralda", area: "Miches, Dominican Republic", bookingUrl: 'https://www.clubmed.co.uk/r/miches-playa-esmeralda/y' },
];

// Mark Warner prices include return flights from London Gatwick.
export const MARKWARNER: Resort[] = [
  { collection: 'markwarner-sun', id: 'paleros-beach-resort', slug: 'paleros', name: 'Paleros', fullName: 'Mark Warner Paleros Beach Resort', area: 'Paleros, Greece', bookingUrl: 'https://www.markwarner.co.uk/sun-holidays/greece/paleros-beach-resort/' },
  { collection: 'markwarner-sun', id: 'aeolian-village', slug: 'aeolian-village', name: 'Aeolian Village', fullName: 'Mark Warner Aeolian Village Beach Resort', area: 'Lesvos, Greece', bookingUrl: 'https://www.markwarner.co.uk/sun-holidays/greece/aeolian-village/' },
  { collection: 'markwarner-sun', id: 'lemnos-beach-resort', slug: 'lemnos', name: 'Lemnos', fullName: 'Mark Warner Lemnos Beach Resort', area: 'Lemnos, Greece', bookingUrl: 'https://www.markwarner.co.uk/sun-holidays/greece/lemnos-beach-resort/' },
  { collection: 'markwarner-sun', id: 'phokaia-beach-resort', slug: 'phokaia', name: 'Phokaia', fullName: 'Mark Warner Phokaia Beach Resort', area: 'Foça, Turkey', bookingUrl: 'https://www.markwarner.co.uk/sun-holidays/turkey/phokaia-beach-resort/' },
];

export const CLUBMED = [...SKI, ...SUN];
export const ALL = [...SKI, ...SUN, ...MARKWARNER];

export const COLLECTIONS: Record<CollectionKey, { brand: string; label: string; base: string; season: 'ski' | 'sun'; featureWeek: string; priceNote: string; bookLabel: string }> = {
  'clubmed-ski': { brand: 'Club Med', label: 'Club Med ski', base: '/club-med/', season: 'ski', featureWeek: 'february-half-term', priceNote: '7 nights, all-inclusive, without flights', bookLabel: 'See it on Club Med' },
  'clubmed-sun': { brand: 'Club Med', label: 'Club Med sun', base: '/club-med/', season: 'sun', featureWeek: 'summer-3', priceNote: '7 nights, all-inclusive, without flights', bookLabel: 'See it on Club Med' },
  'markwarner-sun': { brand: 'Mark Warner', label: 'Mark Warner', base: '/mark-warner/', season: 'sun', featureWeek: 'summer-3', priceNote: '7 nights including return flights from London Gatwick', bookLabel: 'See it on Mark Warner' },
};
