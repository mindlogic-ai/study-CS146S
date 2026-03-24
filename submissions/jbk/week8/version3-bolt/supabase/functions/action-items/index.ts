import { createClient } from 'npm:@supabase/supabase-js@2.57.4';

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, OPTIONS",
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
    const actionItemId = pathParts[pathParts.length - 1];
    const isCompleteEndpoint = pathParts[pathParts.length - 1] === 'complete';
    const actualId = isCompleteEndpoint ? pathParts[pathParts.length - 2] : actionItemId;

    if (req.method === "GET") {
      if (actualId && actualId !== 'action-items') {
        const { data, error } = await supabase
          .from('action_items')
          .select('*')
          .eq('id', actualId)
          .maybeSingle();

        if (error) throw error;
        if (!data) {
          return new Response(JSON.stringify({ error: 'Action item not found' }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }

        return new Response(JSON.stringify(data), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } else {
        const completedParam = url.searchParams.get('completed');
        const skip = parseInt(url.searchParams.get('skip') || '0');
        const limit = parseInt(url.searchParams.get('limit') || '50');
        const sort = url.searchParams.get('sort') || '-createdAt';

        let query = supabase.from('action_items').select('*');

        if (completedParam !== null) {
          const completed = completedParam === 'true';
          query = query.eq('completed', completed);
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
      const { description } = body;

      if (!description) {
        return new Response(JSON.stringify({ error: 'Description is required' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      const { data, error } = await supabase
        .from('action_items')
        .insert({ description, completed: false })
        .select()
        .single();

      if (error) throw error;

      return new Response(JSON.stringify(data), {
        status: 201,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    if (req.method === "PUT" && isCompleteEndpoint) {
      const { data, error } = await supabase
        .from('action_items')
        .update({ completed: true, updated_at: new Date().toISOString() })
        .eq('id', actualId)
        .select()
        .single();

      if (error) throw error;

      return new Response(JSON.stringify(data), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    if (req.method === "PATCH") {
      const body = await req.json();
      const updates: { description?: string; completed?: boolean; updated_at: string } = {
        updated_at: new Date().toISOString()
      };

      if (body.description !== undefined) updates.description = body.description;
      if (body.completed !== undefined) updates.completed = body.completed;

      const { data, error } = await supabase
        .from('action_items')
        .update(updates)
        .eq('id', actualId)
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
