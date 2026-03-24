import { createClient } from 'npm:@supabase/supabase-js@2.57.4';

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PATCH, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_ANON_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const url = new URL(req.url);
    const pathParts = url.pathname.split('/').filter(p => p);
    const noteId = pathParts[pathParts.length - 1];

    if (req.method === "GET") {
      if (noteId && noteId !== 'notes') {
        const { data, error } = await supabase
          .from('notes')
          .select('*')
          .eq('id', noteId)
          .maybeSingle();

        if (error) throw error;
        if (!data) {
          return new Response(JSON.stringify({ error: 'Note not found' }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        return new Response(JSON.stringify(data), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } else {
        const q = url.searchParams.get('q') || '';
        const skip = parseInt(url.searchParams.get('skip') || '0');
        const limit = parseInt(url.searchParams.get('limit') || '50');
        const sort = url.searchParams.get('sort') || '-createdAt';

        let query = supabase.from('notes').select('*');

        if (q) {
          query = query.or(`title.ilike.%${q}%,content.ilike.%${q}%`);
        }

        const descending = sort.startsWith('-');
        const sortField = descending ? sort.substring(1) : sort;
        const dbField = sortField === 'createdAt' ? 'created_at' : sortField === 'updatedAt' ? 'updated_at' : sortField;
        query = query.order(dbField, { ascending: !descending });

        query = query.range(skip, skip + limit - 1);

        const { data, error } = await query;
        if (error) throw error;

        return new Response(JSON.stringify(data), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    if (req.method === "POST") {
      const body = await req.json();
      const { title, content } = body;

      if (!title || !content) {
        return new Response(JSON.stringify({ error: 'Title and content are required' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      const { data, error } = await supabase
        .from('notes')
        .insert({ title, content })
        .select()
        .single();

      if (error) throw error;

      return new Response(JSON.stringify(data), {
        status: 201,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    if (req.method === "PATCH") {
      const body = await req.json();
      const updates: { title?: string; content?: string; updated_at: string } = {
        updated_at: new Date().toISOString()
      };

      if (body.title !== undefined) updates.title = body.title;
      if (body.content !== undefined) updates.content = body.content;

      const { data, error } = await supabase
        .from('notes')
        .update(updates)
        .eq('id', noteId)
        .select()
        .single();

      if (error) throw error;

      return new Response(JSON.stringify(data), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
