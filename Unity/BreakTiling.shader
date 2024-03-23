Shader "Custom/TilingBreak" {
    Properties {
        _MainTex ("Albedo (RGB)", 2D) = "white" {}
        _Color ("Color", Color) = (1,1,1,1)
        _BumpMap ("Normal Map", 2D) = "bump" {}
        _NormalMapInfluence ("Normal Map Influence", Range(0,10)) = 1.0
        _Smoothness ("Smoothness", Range(0,1)) = 0.5
        _Seed ("Seed", Float) = 1.0
        _BlendRange ("Blend Range", Range(0, 1)) = 0.1
        _MinScale ("Minimum Scale", Range(0, 5.0)) = 0.5
        _MaxScale ("Maximum Scale", Range(0, 5.0)) = 2.0
        _OverlayScale ("Overlay Scale", Range(1,15)) = 1.0
        _OverlayOpacity ("Overlay Opacity", Range(0,1)) = 0.5
        _BlendRange2 ("Overlay Blend Range", Range(0, 1)) = 0.1
        [Toggle(DEBUG_MODE)] _DebugMode ("Debug Mode", Float) = 0

    }
    SubShader {
        Tags { "RenderType"="Opaque" }
        LOD 100
        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows
        #pragma multi_compile __ DEBUG_MODE
        #pragma target 3.0
        #pragma shader_feature_local _NORMALMAP
        sampler2D _MainTex;
        sampler2D _BumpMap;
        float4 _Color;
        float _Smoothness;
        float _Seed;
        float _BlendRange;
        float _MinScale;
        float _MaxScale;
        float _NormalMapInfluence;
        float _OverlayScale;
        float _DebugMode;
        float _BlendRange2;
float _OverlayOpacity;
        struct Input {
            float2 uv_MainTex;
            float3 worldPos;
        };
        float3 mod289(float3 x) {
            return x - floor(x * (1.0 / 289.0)) * 289.0;
        }

        float2 mod289(float2 x) {
            return x - floor(x * (1.0 / 289.0)) * 289.0;
        }

        float3 permute(float3 x) {
            return mod289((x * 34.0 + 1.0) * x);
        }

        float3 taylorInvSqrt(float3 r) {
            return 1.79284291400159 - 0.85373472095314 * r;
        }

        // output noise is in range [-1, 1]
        float snoise(float2 v) {
            const float4 C = float4(0.211324865405187,  // (3.0-sqrt(3.0))/6.0
                                    0.366025403784439,  // 0.5*(sqrt(3.0)-1.0)
                                    -0.577350269189626, // -1.0 + 2.0 * C.x
                                    0.024390243902439); // 1.0 / 41.0

            // First corner
            float2 i  = floor(v + dot(v, C.yy));
            float2 x0 = v -   i + dot(i, C.xx);

            // Other corners
            float2 i1;
            i1.x = step(x0.y, x0.x);
            i1.y = 1.0 - i1.x;

            // x1 = x0 - i1  + 1.0 * C.xx;
            // x2 = x0 - 1.0 + 2.0 * C.xx;
            float2 x1 = x0 + C.xx - i1;
            float2 x2 = x0 + C.zz;

            // Permutations
            i = mod289(i); // Avoid truncation effects in permutation
            float3 p =
              permute(permute(i.y + float3(0.0, i1.y, 1.0))
                            + i.x + float3(0.0, i1.x, 1.0));

            float3 m = max(0.5 - float3(dot(x0, x0), dot(x1, x1), dot(x2, x2)), 0.0);
            m = m * m;
            m = m * m;

            // Gradients: 41 points uniformly over a line, mapped onto a diamond.
            // The ring size 17*17 = 289 is close to a multiple of 41 (41*7 = 287)
            float3 x = 2.0 * frac(p * C.www) - 1.0;
            float3 h = abs(x) - 0.5;
            float3 ox = floor(x + 0.5);
            float3 a0 = x - ox;

            // Normalise gradients implicitly by scaling m
            m *= taylorInvSqrt(a0 * a0 + h * h);

            // Compute final noise value at P
            float3 g = float3(
                a0.x * x0.x + h.x * x0.y,
                a0.y * x1.x + h.y * x1.y,
                g.z = a0.z * x2.x + h.z * x2.y
            );
            return 130.0 * dot(m, g);
        }

        float snoise01(float2 v) {
            return snoise(v) * 0.5 + 0.5;
        }
        float2 rotate(float2 uv, float rotation) {
            float s = sin(radians(rotation));
            float c = cos(radians(rotation));
            float2x2 rotationMatrix = float2x2(c, -s, s, c);
            return mul(rotationMatrix, uv - 0.5) + 0.5;
        }
        void surf (Input IN, inout SurfaceOutputStandard o) {
            float2 uv = IN.uv_MainTex;
            float2 tile = floor(uv);
            float2 randomUV = frac(uv);
            // Generate a random rotation and scale for each tile based on the tile position and seed
            float randomRotationValue = snoise(float2(dot(tile, float2(12.9898, 78.233)) + _Seed, 0.0));
            float rotation = randomRotationValue * 360.0; // Use snoise for rotation
            float randomScaleValue = snoise01(float2(dot(tile, float2(4.9812, 79.123)) + _Seed, 1.0));
            float scale = lerp(_MinScale, _MaxScale, randomScaleValue); // Use snoise01 for scale


            // Apply scale and rotation adjustments to the UVs
            float2 center = float2(0.5, 0.5);

            // Blend edges for each tile
            float2 edgeBlendUV = frac(uv);
            // Improved edge blending calculation
            float edgeDistanceX = min(edgeBlendUV.x, 1.0 - edgeBlendUV.x);
            float edgeDistanceY = min(edgeBlendUV.y, 1.0 - edgeBlendUV.y);
            float edgeDistance = min(edgeDistanceX, edgeDistanceY);
            float edgeBlend = smoothstep(0.0, _BlendRange, edgeDistance);

            // Modify here for different rotation on the edge blend
            float edgeRotation = snoise01(float2(dot(tile, float2(12.9898, 78.233)) + _Seed + 1.0, 2.0)) * 360.0;

            float2 edgeUV = rotate(edgeBlendUV, edgeRotation); // Apply distinct rotation for edges

            edgeUV = (edgeUV - center) * scale + center; // Apply scale

            // Sample textures with original UVs and edge UVs for blending
            fixed4 texColor = tex2D(_MainTex, randomUV) * _Color;
            fixed4 edgeColor = tex2D(_MainTex, edgeUV) * _Color; // Corrected to sample edge color with the edge UVs after rotation

            // Blend edge color with tile color based on the blend range
            float2 overlayTile = floor(uv / _OverlayScale);
            float2 overlayRandomTile = frac(uv / _OverlayScale);
            fixed4 baseBlend = lerp(texColor, edgeColor, edgeBlend);
            float overlayRotation = snoise(float2(dot(overlayTile, float2(12.3412, 54.123)) + _Seed, 5.0)) * 360.0; // Unique rotation for overlay
            float2 overlayUV = rotate(overlayRandomTile, overlayRotation); // Apply rotation for overlay

            fixed4 overlayColor = tex2D(_MainTex, overlayUV) * _Color; // Sample overlay texture

            // Improved edge blending calculation
            float edgeDistanceXOvr = min(overlayUV.x, 1.0 - overlayUV.x);
            float edgeDistanceYOvr = min(overlayUV.y, 1.0 - overlayUV.y);
            float edgeDistanceOvr = min(edgeDistanceXOvr, edgeDistanceYOvr);

            float edgeBlendOverlay = smoothstep(0.0, _BlendRange2, edgeDistanceOvr);

            fixed4 overlayEdgeColor = tex2D(_MainTex, overlayRandomTile);
            fixed4 overlayBlended = lerp(overlayEdgeColor,overlayColor, edgeBlendOverlay);
            fixed4 baseAndOverlay = lerp(baseBlend,overlayBlended, _OverlayOpacity); // Blend with base texture
            
            // Add this inside your surf function, after calculating baseBlend but before applying it to o.Albedo
            fixed4 debugColor = fixed4(0,0,0,1); // Black color to initialize

            // Detect if we are close to the edge of a tile
            float isNearEdge = step(0.05, edgeDistance); // 0.05 is a threshold, can be adjusted

            // Assign a bright color for visualization where artifacts are detected
            if (isNearEdge < 1.0) {
                debugColor = fixed4(1,0,0,1); // Red color for visual debugging
            }

            // Now blend this with your baseAndOverlay based on the debug flag
            #ifdef DEBUG_MODE
            o.Albedo = lerp(baseBlend.rgb, debugColor.rgb, debugColor.a);
            #else
            o.Albedo = baseAndOverlay.rgb;
            #endif

            o.Alpha = 1;
            o.Smoothness = _Smoothness;

            #ifdef _NORMALMAP
            float blendFactor = smoothstep(0.0, 1.0, edgeBlend); // Adjust the blend factor based on 
            fixed3 bumpMap = UnpackNormal(tex2D(_BumpMap, randomUV));
            fixed3 edgeBumpMap = UnpackNormal(tex2D(_BumpMap, edgeUV));
            // Use the _NormalMapInfluence to adjust the final normal map effect
            fixed3 neutralNormal = float3(0.5, 0.5, 1); // Represents a neutral normal map
            fixed3 blendedBump = lerp(bumpMap, edgeBumpMap, blendFactor);
            fixed3 finalBump = lerp(neutralNormal, blendedBump, _NormalMapInfluence); // Adjust with influence

            o.Normal = finalBump;
            #endif
        }
        ENDCG
    }
    FallBack "Diffuse"
}
